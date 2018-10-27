extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern void __VERIFIER_assume(int);
extern int __VERIFIER_nondet_float();
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }

typedef enum { false = 0, true = 1 } bool;

#define EPSILON epsilon

int sparsevector(float epsilon, float T, int N, int size, float q[])
{
  __VERIFIER_assume(epsilon > 0);
  __VERIFIER_assume(size > 0);
  float dq[size];
  for(int i = 0; i < size; i++)
    dq[i] = __VERIFIER_nondet_float();
  float v_epsilon = 0;


  float eta_1 = __VERIFIER_nondet_float();
  float s_eta_1 = eta_1;
  v_epsilon = v_epsilon + EPSILON / 2;

  float T_bar = T + eta_1;
  int c_1 = 0, c_2 = 0;
  int i = 0;
  bool out = false;

  while (c_1 < N && i < size)
  {
    float eta_2 = __VERIFIER_nondet_float();
    float s_eta_2 = eta_2;
    v_epsilon = (q[i] + eta_2 >= T_bar) ? (0 + 2 * EPSILON / 2.0) : (v_epsilon + 0) ;

    if (q[i] + eta_2 >= T_bar)
    {
      __VERIFIER_assume(dq[i] <= 1 && -1 <= dq[i]);
      __VERIFIER_assert(q[i] + dq[i] + eta_2 + 2 >= T_bar + 1);
      out = true;
      c_1 = c_1 + 1;
    }
    else
    {
      __VERIFIER_assume(dq[i] <= 1 && -1 <= dq[i]);
      __VERIFIER_assert(q[i] + dq[i] + eta_2 < T_bar + 1);
      out = false;
      c_2 = c_2 + 1;
    }
    i = i + 1;
  }
  __VERIFIER_assert(v_epsilon <= EPSILON);
}
