# MIT License
#
# Copyright (c) 2018-2019 Yuxin (Ryan) Wang
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sympy as sp
import logging
import copy
from pycparser import c_ast
from pycparser.c_generator import CGenerator
from pycparser.c_ast import NodeVisitor
from shadowdp.types import TypeSystem, convert_to_ast, is_node_equal
logger = logging.getLogger(__name__)

_code_generator = CGenerator()


class _ExpressionFinder(NodeVisitor):
    """ this class find a specific node in the expression"""
    def __init__(self, check_func):
        self._check_func = check_func

    def generic_visit(self, node):
        if self._check_func(node):
            return node
        else:
            for child in node:
                node = self.generic_visit(child)
                if node:
                    return node


class _ShadowBranchGenerator(NodeVisitor):
    """ this class generates the shadow branch statement"""
    def __init__(self, shadow_variables, types, conditions):
        """
        :param shadow_variables: the variable list whose shadow distances should be updated
        """
        self._shadow_variables = shadow_variables
        self._distance_generator = _DistanceGenerator(types, conditions)

    # TODO: currently doesn't support declaration in branch
    def visit_Decl(self, node):
        raise NotImplementedError

    def visit_Compound(self, node):
        # TODO: currently doesn't support ArrayRef
        # remove those assignments which has no
        node.block_items = [child for child in node.block_items
                            if isinstance(child, c_ast.Assignment) and child.lvalue.name in self._shadow_variables]
        for child in node:
            if isinstance(child, c_ast.Assignment):
                child.lvalue.name = '__LANG_distance_shadow_{}'.format(child.lvalue.name)
                child.rvalue = convert_to_ast(self._distance_generator.visit(child.rvalue)[1])
            else:
                self.visit(child)


class _ExpressionReplacer(NodeVisitor):
    def __init__(self, types, is_aligned, conditions):
        assert isinstance(types, TypeSystem)
        self._types = types
        self._is_aligned = is_aligned
        self._conditions = conditions

    def _replace(self, node):
        if isinstance(node, c_ast.ArrayRef):
            alignd, shadow = self._types.get_distance(node.name.name, self._conditions)
            distance = alignd if self._is_aligned else shadow
            if distance == '0':
                return node
            else:
                return c_ast.BinaryOp(op='+',
                                      left=node,
                                      right=c_ast.ArrayRef(name=c_ast.ID(name=distance),
                                                           subscript=node.subscript))
        elif isinstance(node, c_ast.ID):
            aligned, shadow = self._types.get_distance(node.name, self._conditions)
            distance = aligned if self._is_aligned else shadow
            if distance == '0':
                return node
            else:
                return c_ast.BinaryOp(op='+',
                                      left=node,
                                      right=c_ast.ID(name=aligned if self._is_aligned else shadow))
        else:
            raise NotImplementedError

    def visit_BinaryOp(self, node):
        if isinstance(node.left, (c_ast.ArrayRef, c_ast.ID)):
            node.left = self._replace(node.left)
        else:
            self.visit(node.left)

        if isinstance(node.right, (c_ast.ArrayRef, c_ast.ID)):
            node.right = self._replace(node.right)
        else:
            self.visit(node.right)

    def visit_UnaryOp(self, node):
        if isinstance(node.expr, (c_ast.ArrayRef, c_ast.ID)):
            node.expr = self._replace(node.expr)
        else:
            self.visit(node.expr)

    def visit(self, node):
        super().visit(node)
        return node


class _ExpressionSimplifier(NodeVisitor):
    """ this class simplifes Ternary operations, e.g., e?c1:c2 + e?c3:c4 -> e?(c1+c2):(c3+c4) """
    def visit_BinaryOp(self, n):
        if isinstance(n.left, c_ast.TernaryOp) and isinstance(n.right, c_ast.TernaryOp) and is_node_equal(n.left.cond, n.right.cond):
            return c_ast.TernaryOp(cond=n.left.cond,
                                   iftrue=c_ast.BinaryOp(op=n.op, left=n.left.iftrue, right=n.right.iftrue),
                                   iffalse=c_ast.BinaryOp(op=n.op, left=n.left.iffalse, right=n.right.iffalse))
        return n

    def visit_TernaryOp(self, n):
        # TODO
        return n

    def visit_UnaryOp(self, n):
        # TODO
        return n

    def simplify(self, expression):
        ast = convert_to_ast(expression)
        return self.visit(ast)


class _DistanceGenerator(NodeVisitor):
    def __init__(self, types, conditions):
        self._types = types
        self._conditions = conditions
        assert isinstance(self._types, TypeSystem)

    def try_simplify(self, expr):
        from sympy import simplify
        try:
            expr = str(simplify(expr))
        finally:
            return expr

    def generic_visit(self, node):
        raise NotImplementedError

    def visit_Constant(self, n):
        return ['0', '0']

    def visit_ID(self, n):
        return self._types.get_distance(n.name, self._conditions)

    def visit_ArrayRef(self, n):
        aligned, shadow = self._types.get_distance(n.name.name, self._conditions)
        aligned += '[{}]'.format(_code_generator.visit(n.subscript))
        shadow += '[{}]'.format(_code_generator.visit(n.subscript))
        return [aligned, shadow]

    def visit_BinaryOp(self, n):
        return [self.try_simplify('{} {} {}'.format(left, n.op, right))
                for left, right in zip(self.visit(n.left), self.visit(n.right))]


class ShadowDPTransformer(NodeVisitor):
    """ Traverse the AST and do necessary transformations on the AST according to the typing rules."""
    def __init__(self, function_map=None, set_epsilon=None):
        """ Initialize the transformer.
        :param function_map: A dict containing a mapping from logical commands (assert / assume / havoc)
        to actual commands (e.g., __VERIFIER_assert in CPAChecker), this is an abstraction for use with other
        verification tools that may have other names for assert / assume / havoc commands.
        :param set_epsilon: boolean value indicating if we want to set epsilon to 1 to overcome the non-linearity issue.
        """
        super().__init__()

        # set default value for function_map
        if not function_map:
            self._func_map = {
                'assert': 'assert',
                'assume': 'assume',
                'havoc': 'havoc',
            }
        else:
            if not isinstance(function_map, dict):
                raise ValueError
            if not ('assert' in function_map and 'assume' in function_map and 'havoc' in function_map):
                raise ValueError
            self._func_map = function_map

        self._set_epsilon = set_epsilon
        self._types = TypeSystem()
        self._parameters = []
        self._random_variables = set()
        # use a stack to keep track of the conditions so that we know we're inside a true branch or false branch
        self._condition_stack = []
        # we keep tracks of the parent of each node since pycparser doesn't provide this feature, this is useful
        # for easy trace back
        self._parents = {}
        # indicate if the transformation should be done
        # this is needed since in While statement we might do loop until convergence, in that case we don't need to
        # do transformation
        self._is_to_transform = True
        # this is needed if we add some statements next to the current statement
        # e.g. float eta = havoc(); _v_epsilon = ...;
        # we shouldn't visit the `_v_epsilon = ...;` statement node, so we keep track of the inserted statements
        # to avoid them
        self._inserted = set()

    def visit(self, node):
        if node in self._inserted:
            # ignore the inserted statement
            return
        for child in node:
            self._parents[child] = node
        return super().visit(node)

    def visit_Assignment(self, node):
        code = _code_generator.visit(node)
        logger.debug('{}'.format(code))
        distance_generator = _DistanceGenerator(self._types, self._condition_stack)
        aligned, shadow = distance_generator.visit(node.rvalue)
        self._types.update_distance(node.lvalue.name, aligned, shadow)
        logger.debug('types: {}'.format(self._types))

    def visit_FuncDef(self, node):
        # the start of the transformation
        self._types.clear()
        logger.info('Start transforming function {} ...'.format(node.decl.name))
        self.generic_visit(node)

        epsilon, size, q, *_ = self._parameters

        inserted = [
            # insert assume(epsilon > 0)
            c_ast.FuncCall(c_ast.ID(self._func_map['assume']),
                           args=c_ast.ExprList([c_ast.BinaryOp('>', c_ast.ID(epsilon),
                                                               c_ast.Constant('int', 0))])),
            # insert assume(size > 0)
            c_ast.FuncCall(c_ast.ID(self._func_map['assume']),
                           args=c_ast.ExprList([c_ast.BinaryOp('>', c_ast.ID(size),
                                                               c_ast.Constant('int', 0))])),
            # insert assume(__LANG_index >= 0);
            c_ast.FuncCall(c_ast.ID(self._func_map['assume']),
                           args=c_ast.ExprList([c_ast.BinaryOp('>=', c_ast.ID('__LANG_index'),
                                                               c_ast.Constant('int', 0))])),

            # insert assume(__LANG_index < size);
            c_ast.FuncCall(c_ast.ID(self._func_map['assume']),
                           args=c_ast.ExprList([c_ast.BinaryOp('<', c_ast.ID('__LANG_index'),
                                                               c_ast.ID(size))])),

            # insert float __LANG_v_epsilon = 0;
            c_ast.Decl(name='__LANG_v_epsilon',
                       type=c_ast.TypeDecl(declname='__LANG_v_epsilon',
                                           type=c_ast.IdentifierType(names=['float']),
                                           quals=[]),
                       init=c_ast.Constant('int', '0'),
                       quals=[], funcspec=[], bitsize=[], storage=[]),
        ]

        for name, is_align in self._types.dynamic_variables():
            if name not in self._parameters:
                distance_name = '__LANG_distance_{}{}'.format('' if is_align else 'shadow_', name)
                inserted.append(c_ast.Decl(name=distance_name,
                                           type=c_ast.TypeDecl(declname=distance_name,
                                                               type=c_ast.IdentifierType(names=['float']),
                                                               quals=[]),
                                           init=c_ast.Constant('int', '0'),
                                           quals=[], funcspec=[], bitsize=[], storage=[]))
            elif name == q and is_align:
                # insert parameter __LANG_distance_q
                node.decl.type.args.params.append(
                    c_ast.Decl(name='__LANG_distance_{}'.format(q),
                               type=c_ast.ArrayDecl(type=c_ast.TypeDecl(declname='__LANG_distance_{}'
                                                                        .format(q),
                                                                        type=c_ast.IdentifierType(
                                                                            names=['float']),
                                                                        quals=[]),
                                                    dim=None,
                                                    dim_quals=[]),
                               init=None,
                               quals=[], funcspec=[], bitsize=[], storage=[])
                )
                # insert parameter __LANG_index
                node.decl.type.args.params.append(
                    c_ast.Decl(name='__LANG_index',
                               type=c_ast.TypeDecl(declname='__LANG_index',
                                                   type=c_ast.IdentifierType(names=['int']),
                                                   quals=[]),
                               init=None,
                               quals=[], funcspec=[], bitsize=[], storage=[])
                )

        node.body.block_items[:0] = inserted

        # insert assert(__LANG_v_epsilon <= epsilon);
        epsilon_node = c_ast.Constant(type='float', value=1.0) if self._set_epsilon else c_ast.ID(epsilon)
        node.body.block_items.append(c_ast.FuncCall(c_ast.ID(self._func_map['assert']),
                                                    args=c_ast.ExprList([c_ast.BinaryOp('<=', c_ast.ID('__LANG_v_epsilon'),
                                                                                     epsilon_node)])), )

    def visit_Decl(self, n):
        logger.debug('{}'.format(_code_generator.visit_Decl(n)))

        decl_type = n.type
        if isinstance(decl_type, c_ast.FuncDecl):
            # put parameters into type system
            for i, decl in enumerate(decl_type.args.params):
                self._parameters.append(decl.name)
                # TODO: this should be filled by annotation on the argument
                if isinstance(decl.type, c_ast.TypeDecl):
                    self._types.update_distance(decl.name, '0', '0')
                elif isinstance(decl.type, c_ast.ArrayDecl) and i == 2:
                    self._types.update_distance(decl.name, '*'.format(decl.name), '__LANG_distance_{}'.format(decl.name))
            logger.debug('Params: {}'.format(self._parameters))
        if isinstance(decl_type, c_ast.TypeDecl):
            # put variable declaration into type system
            if n.init:
                if isinstance(n.init, c_ast.FuncCall):
                    if n.init.name.name == 'Lap':
                        # random variable declaration
                        self._random_variables.add(n.name)
                        logger.debug('Random variables: {}'.format(self._random_variables))
                        sample = _code_generator.visit(n.init.args.exprs[0])
                        assert isinstance(n.init.args.exprs[1], c_ast.Constant) and \
                               n.init.args.exprs[1].type == 'string', \
                            'The second argument of Lap function must be string annotation'
                        s_e, s_d, d_eta, *_ = map(lambda x: x.strip(), n.init.args.exprs[1].value[1:-1].split(';'))
                        # set the random variable distance
                        self._types.update_distance(n.name, s_d.replace('ALIGNED', d_eta).replace('SHADOW', '0'), '0')
                        # set the normal variable distances
                        for name in self._types.names():
                            if name not in self._random_variables and name not in self._parameters:
                                aligned, shadow = self._types.get_distance(name, self._condition_stack)
                                # if the aligned distance and shadow distance are the same
                                # then there's no need to update the distances
                                if aligned == shadow:
                                    continue
                                else:
                                    self._types.update_distance(name,
                                                                s_e.replace('ALIGNED', '({})'.format(aligned))
                                                                .replace('SHADOW', '({})'.format(shadow)),
                                                                shadow)
                        if self._is_to_transform:
                            n.init = c_ast.FuncCall(c_ast.ID(self._func_map['havoc']), args=None)
                            assert isinstance(self._parents[n], c_ast.Compound)
                            n_index = self._parents[n].block_items.index(n)
                            # incorporate epsilon = 1 approach
                            if self._set_epsilon:
                                epsilon, *_ = self._parameters
                                sample = sample.replace(epsilon, '1.0')
                            cost = '({} * (1/({})))'.format(d_eta, sample)
                            # try simplify the cost expression
                            try:
                                cost = str(sp.simplify(cost))
                            except:
                                pass
                            finally:
                                pass

                            v_epsilon = '({}) + ({})'.format(s_e.replace('ALIGNED', '__LANG_v_epsilon').replace('SHADOW', '0'),
                                                             s_d.replace('ALIGNED', cost).replace('SHADOW', '0'))
                            simplifier = _ExpressionSimplifier()
                            update_v_epsilon = c_ast.Assignment(op='=',
                                                                lvalue=c_ast.ID('__LANG_v_epsilon'),
                                                                rvalue=simplifier.simplify(v_epsilon))
                            self._parents[n].block_items.insert(n_index + 1, update_v_epsilon)
                            self._inserted.add(update_v_epsilon)

                    else:
                        # TODO: function call currently not supported
                        raise NotImplementedError
                else:
                    distance_generator = _DistanceGenerator(self._types, self._condition_stack)
                    aligned, shadow = distance_generator.visit(n.init)
                    self._types.update_distance(n.name, aligned, shadow)
            else:
                self._types.update_distance(n.name, '0', '0')

        elif isinstance(decl_type, c_ast.ArrayDecl):
            # put array variable declaration into type dict
            # TODO: fill in the type
            self._types.update_distance(n.name, '0', '0')

        logger.debug('types: {}'.format(self._types))

    def visit_If(self, n):
        self.visit(n.cond)
        logger.debug('types(before branch): {}'.format(self._types))
        logger.debug('if({})'.format(_code_generator.visit(n.cond)))
        before_types = self._types.copy()
        self._condition_stack.append([n.cond, True])
        # to be used in if branch transformation assert(e^aligned);
        aligned_true_cond = _ExpressionReplacer(before_types, True, self._condition_stack).visit(
            copy.deepcopy(n.cond))
        self.visit(n.iftrue)
        true_types = self._types
        logger.debug('types(true branch): {}'.format(true_types))
        self._types = before_types.copy()
        logger.debug('else')
        self._condition_stack[-1][1] = False
        if n.iffalse:
            self.visit(n.iffalse)
        # to be used in else branch transformation assert(not (e^aligned));
        aligned_false_cond = _ExpressionReplacer(before_types, True, self._condition_stack).visit(
            copy.deepcopy(n.cond))
        logger.debug('types(false branch): {}'.format(self._types))
        false_types = self._types.copy()
        self._types.merge(true_types)
        logger.debug('types(after merge): {}'.format(self._types))
        # TODO: use Z3 to solve constraints to decide this value
        to_generate_shadow = True
        if self._is_to_transform:
            # have to generate separate shadow branch
            if to_generate_shadow:
                shadow_cond = _ExpressionReplacer(self._types, False, self._condition_stack).visit(
                    copy.deepcopy(n.cond))
                parent = self._parents[n]
                n_index = parent.block_items.index(n)
                shadow_branch = c_ast.If(cond=shadow_cond,
                                         iftrue=c_ast.Compound(
                                             block_items=copy.deepcopy(n.iftrue.block_items)),
                                         iffalse=c_ast.Compound(
                                             block_items=copy.deepcopy(n.iffalse.block_items)) if n.iffalse else None)
                shadow_branch_generator = _ShadowBranchGenerator(
                    {name for name, is_aligned in self._types.dynamic_variables() if not is_aligned},
                    self._types,
                    self._condition_stack)
                shadow_branch_generator.visit(shadow_branch)
                self._inserted.add(shadow_branch)
                parent.block_items.insert(n_index + 1, shadow_branch)

            # insert assertion
            n.iftrue.block_items.insert(0, c_ast.FuncCall(name=c_ast.ID(self._func_map['assert']),
                                                          args=c_ast.ExprList(exprs=[aligned_true_cond])))

            # if the expression contains `query` variable, add an assume function on dq
            exp_checker = _ExpressionFinder(
                lambda node: isinstance(node, c_ast.ArrayRef) and
                             node.name.name == '__LANG_distance_{}'.format(self._parameters[2]))
            query_distance_node = exp_checker.visit(aligned_true_cond)
            if query_distance_node:
                # insert assume(__LANG_distance_q[i] >= -1 && __LANG_distance_q[i] <= 1)
                # TODO: should change according to programmer
                assume_function = \
                    c_ast.FuncCall(name=c_ast.ID(self._func_map['assume']),
                                   args=c_ast.ExprList(
                                       exprs=[c_ast.BinaryOp(op='&&',
                                                             left=c_ast.BinaryOp(op='>=',
                                                                                 left=query_distance_node,
                                                                                 right=c_ast.Constant('int', '-1')),
                                                             right=c_ast.BinaryOp(op='<=',
                                                                                  left=query_distance_node,
                                                                                  right=c_ast.Constant('int', '1')))]))
                n.iftrue.block_items.insert(0, assume_function)

            for name, is_aligned in self._types.diff(true_types):
                if is_aligned:
                    n.iftrue.block_items.append(c_ast.Assignment(op='=',
                                                                 lvalue=c_ast.ID('__LANG_distance_{}'.format(name)),
                                                                 rvalue=true_types.get_raw_distance(name)[0]))
            # create else branch if doesn't exist
            n.iffalse = n.iffalse if n.iffalse else c_ast.Compound(block_items=[])
            # add assume to else branch
            # insert assertion
            n.iffalse.block_items.insert(0, c_ast.FuncCall(name=c_ast.ID(self._func_map['assert']),
                                                           args=c_ast.ExprList(exprs=[
                                                               c_ast.UnaryOp(op='!', expr=aligned_false_cond)
                                                           ])))
            query_distance_node = exp_checker.visit(aligned_false_cond)
            if query_distance_node:
                # insert assume(__LANG_distance_q[i] >= -1 && __LANG_distance_q[i] <= 1)
                # TODO: should change according to programmer
                assume_function = \
                    c_ast.FuncCall(name=c_ast.ID(self._func_map['assume']),
                                   args=c_ast.ExprList(
                                       exprs=[c_ast.BinaryOp(op='&&',
                                                             left=c_ast.BinaryOp(op='>=',
                                                                                 left=query_distance_node,
                                                                                 right=c_ast.Constant('int', '-1')),
                                                             right=c_ast.BinaryOp(op='<=',
                                                                                  left=query_distance_node,
                                                                                  right=c_ast.Constant('int', '1')))]))
                n.iffalse.block_items.insert(0, assume_function)
            for name, is_aligned in self._types.diff(false_types):
                if is_aligned:
                    n.iffalse.block_items.append(c_ast.Assignment(op='=',
                                                                  lvalue=c_ast.ID('__LANG_distance_{}'.format(name)),
                                                                  rvalue=false_types.get_raw_distance(name)[0]))

        self._condition_stack.pop()

    def visit_While(self, node):
        cur_types = None
        # don't output while doing iterations
        logger.disabled = True
        self._is_to_transform = False
        while cur_types != self._types:
            cur_types = self._types.copy()
            self.generic_visit(node)
            self._types.merge(cur_types)
        logger.disabled = False
        self._is_to_transform = True
        logger.debug('while({})'.format(_code_generator.visit(node.cond)))
        logger.debug('types(fixed point): {}'.format(self._types))
        aligned_cond = _ExpressionReplacer(self._types, True, self._condition_stack).visit(
            copy.deepcopy(node.cond))
        assertion = c_ast.FuncCall(name=c_ast.ID(self._func_map['assert']),
                                   args=c_ast.ExprList(exprs=[aligned_cond]))
        self._inserted.add(assertion)
        node.stmt.block_items.insert(0, assertion)
        self.generic_visit(node)
