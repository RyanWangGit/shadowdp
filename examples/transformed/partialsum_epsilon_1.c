extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;

int partialsum_epsilon_1(float epsilon, int size, float q[], float __DP_ALIGNED_q[], float __DP_SHADOW_q[], int __DP_index)
{
  __VERIFIER_assume(epsilon > 0);
  __VERIFIER_assume(size > 0);
  __VERIFIER_assume(__DP_index >= 0);
  __VERIFIER_assume(__DP_index < size);

  float __DP_v_epsilon = 0;
  float __DP_ALIGNED_sum;

  float out = 0;
  float sum = 0;
  int i = 0;

  __DP_ALIGNED_sum = sum;
  while (i < size)
  {
    __VERIFIER_assert(i < size);
    if (i == __DP_index)
    {
      __VERIFIER_assume((__DP_ALIGNED_q[i] - q[i]) >= -1);
      __VERIFIER_assume((__DP_ALIGNED_q[i] - q[i]) <= 1);
    }
    else
    {
      __VERIFIER_assume((__DP_ALIGNED_q[i] - q[i]) == 0);
    }
    sum = sum + q[i];
    __DP_ALIGNED_sum = __DP_ALIGNED_sum + (__DP_ALIGNED_q[i] - q[i]);
    i = i + 1;
  }

  float eta = __VERIFIER_nondet_float();
  __DP_v_epsilon = __DP_v_epsilon + __DP_ALIGNED_sum;
  out = sum + eta;
  __VERIFIER_assert(__DP_v_epsilon <= 1);
}
