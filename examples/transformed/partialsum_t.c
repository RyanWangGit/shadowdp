extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;

int partialsum(float epsilon, int size, float q[], float __LANG_distance_q[], int __LANG_index)
{
  __VERIFIER_assume(epsilon >= 0);
  __VERIFIER_assume(size > 0);
  __VERIFIER_assume(__LANG_index >= 0 && __LANG_index < size);

  float __LANG_v_epsilon = 0;
  float __LANG_distance_sum = 0;
  float out = 0;
  float sum = 0;
  int i = 0;
  while (i < size)
  {
    __VERIFIER_assert(i < size);
    if (i == __LANG_index)
        __VERIFIER_assume (__LANG_distance_q[i] >= -1 && __LANG_distance_q[i] <= 1);
    else
        __VERIFIER_assume (__LANG_distance_q[i] == 0);
    sum = sum + q[i];
    __LANG_distance_sum = __LANG_distance_sum + __LANG_distance_q[i];
    i = i + 1;
  }

  float eta = __VERIFIER_nondet_float();
  __VERIFIER_assert(__LANG_distance_sum <= 1);
  __LANG_v_epsilon = __LANG_v_epsilon + (epsilon);
  out = sum + eta;
  __VERIFIER_assert(__LANG_v_epsilon <= epsilon);
}
