extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;
    
int noisymax(float epsilon, int size, float q[], float __DP_ALIGNED_q[], float __DP_SHADOW_q[])
{
  __VERIFIER_assume(epsilon > 0);
  __VERIFIER_assume(size > 0);
  float __DP_v_epsilon = 0;
  float __DP_ALIGNED_bq;
  float __DP_SHADOW_bq;

  int max = 0;
  int i = 0;
  float bq = 0;

  __DP_ALIGNED_bq = bq; __DP_SHADOW_bq = bq;
  while (i < size)
  {
    __VERIFIER_assert(i < size);
    float eta = __VERIFIER_nondet_float();
    __DP_v_epsilon = (((q[i] + eta) > bq) || (i == 0)) ? (0 + epsilon) : (__DP_v_epsilon + 0);
    if (((q[i] + eta) > bq) || (i == 0))
    {
      __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] >= -1);
      __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] <= 1);
      __VERIFIER_assume(__DP_SHADOW_q[i] == __DP_ALIGNED_q[i]);
      __VERIFIER_assert(((q[i] + (__DP_ALIGNED_q[i] - q[i]) + eta + 2) > __DP_SHADOW_bq) || (i == 0));
      max = i;
      bq = q[i] + eta;
      __DP_ALIGNED_bq = bq + (__DP_ALIGNED_q[i] - q[i]) + 2;
    }
    else
    {
      __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] >= -1);
      __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] <= 1);
      __VERIFIER_assume(__DP_SHADOW_q[i] == __DP_ALIGNED_q[i]);
      __VERIFIER_assert(!(((q[i] + (__DP_ALIGNED_q[i] - q[i]) + eta) > __DP_ALIGNED_bq || (i == 0))));
    }

    __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] >= -1);
    __VERIFIER_assume(__DP_ALIGNED_q[i] - q[i] <= 1);
    __VERIFIER_assume(__DP_SHADOW_q[i] == __DP_ALIGNED_q[i]);
    if ((__DP_SHADOW_q[i] + eta) > __DP_SHADOW_bq || (i == 0))
    {
      __DP_SHADOW_bq = __DP_SHADOW_q[i] + eta;
    }

    i = i + 1;
  }

  __VERIFIER_assert(__DP_v_epsilon <= epsilon);
}

