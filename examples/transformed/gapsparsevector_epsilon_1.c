extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;


int gapsparsevector_epsilon_1(float epsilon, int size, float q[], float T, float __DP_ALIGNED_q[], float __DP_SHADOW_q[])
{
  __VERIFIER_assume(epsilon > 0);
  __VERIFIER_assume(size > 0);
  float __DP_v_epsilon = 0;

  int out = 0;
  float eta_1 = __VERIFIER_nondet_float();
  __DP_v_epsilon = __DP_v_epsilon + (0.5 * 1);
  float T_bar = T + eta_1;
  int c_1 = 0;
  int c_2 = 0;
  int i = 0;

  while ((c_1 < 1) && (i < size))
  {
    __VERIFIER_assert((c_1 < 1) && (i < size));
    float eta_2 = __VERIFIER_nondet_float();

    __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] >= -1);
    __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] <= 1);
    __VERIFIER_assume(__DP_SHADOW_q[i] == __DP_ALIGNED_q[i]);
    __VERIFIER_assert(1 - (__DP_ALIGNED_q[i] - q[i]) <= 2);
    __DP_v_epsilon = __DP_v_epsilon + (((q[i] + eta_2) >= T_bar) ? (0.5 * 1) : (0));
    if ((q[i] + eta_2) >= T_bar)
    {
      __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] >= -1);
      __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] <= 1);
      __VERIFIER_assume(__DP_SHADOW_q[i] == __DP_ALIGNED_q[i]);
      __VERIFIER_assert((__DP_ALIGNED_q[i] + eta_2 + 2) >= (T_bar + 1));
      out = (q[i] + eta_2) - T_bar;
      c_1 = c_1 + 1;
    }
    else
    {
      __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] >= -1);
      __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] <= 1);
      __VERIFIER_assume(__DP_SHADOW_q[i] == __DP_ALIGNED_q[i]);
      __VERIFIER_assert(!((__DP_ALIGNED_q[i] + eta_2) >= (T_bar + 1)));
      out = 0;
      c_2 = c_2 + 1;
    }

    i = i + 1;
  }

  __VERIFIER_assert(__DP_v_epsilon <= 1);
}
