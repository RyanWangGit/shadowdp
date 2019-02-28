extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;

void smartsum_epsilon_1(float epsilon, int size, float q[], int T, int M, float __DP_ALIGNED_q[], float __DP_SHADOW_q[], int __DP_index)
{
  __VERIFIER_assume(size > 0);
  __VERIFIER_assume(T < size && T > 0);
  __VERIFIER_assume(M > 0 && M < size);
  __VERIFIER_assume(__DP_index >= 0);
  __VERIFIER_assume(__DP_index < size);

  float __DP_v_epsilon = 0;
  float __DP_ALIGNED_sum;

  float out = 0;
  float next = 0;
  float n = 0;
  int i = 0;
  float sum = 0;

  __DP_ALIGNED_sum = sum;
  while (i <= T && i < size)
  {
    __VERIFIER_assert(i <= T && i < size);

    if (((i + 1) % M) == 0)
    {
      __VERIFIER_assert(((i + 1) % M) == 0);
      float eta_1 = __VERIFIER_nondet_float();
      if (i == __DP_index)
      {
        __VERIFIER_assume((__DP_ALIGNED_q[i] - q[i]) >= -1);
        __VERIFIER_assume((__DP_ALIGNED_q[i] - q[i]) <= 1);
      }
      else
      {
        __VERIFIER_assume((__DP_ALIGNED_q[i] - q[i]) == 0);
      }
      __DP_v_epsilon = __DP_v_epsilon + abs(__DP_ALIGNED_sum - sum + __DP_ALIGNED_q[i] - q[i]);
      n = n + sum + q[i] + eta_1;
      next = n;
      sum = 0;
      out = next;
      __DP_ALIGNED_sum = sum;
    }
    else
    {
      __VERIFIER_assert(!(((i + 1) % M) == 0));
      float eta_2 = __VERIFIER_nondet_float();
      if (i == __DP_index)
      {
        __VERIFIER_assume((__DP_ALIGNED_q[i] - q[i]) >= -1);
        __VERIFIER_assume((__DP_ALIGNED_q[i] - q[i]) <= 1);
      }
      else
      {
        __VERIFIER_assume((__DP_ALIGNED_q[i] - q[i]) == 0);
      }
      __DP_v_epsilon = __DP_v_epsilon + abs(__DP_ALIGNED_q[i] - q[i]);
      next = next + q[i] + eta_2;
      sum = sum + q[i];
      out = next;
      __DP_ALIGNED_sum = __DP_ALIGNED_sum + __DP_ALIGNED_q[i];
    }
    i = i + 1;
  }

  __VERIFIER_assert(__DP_v_epsilon <= 2);
}
