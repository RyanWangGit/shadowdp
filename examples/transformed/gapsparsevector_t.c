extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define Abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;
    
int gapsparsevector(float epsilon, int size, float q[], float T, float __SHADOWDP_ALIGNED_DISTANCE_q[], float __SHADOWDP_SHADOW_DISTANCE_q[])
{
  __VERIFIER_assume(epsilon > 0);
  __VERIFIER_assume(size > 0);
  float __SHADOWDP_v_epsilon = 0;
  float __SHADOWDP_SHADOW_DISTANCE_out = 0;
  float __SHADOWDP_SHADOW_DISTANCE_c_1 = 0;
  float __SHADOWDP_SHADOW_DISTANCE_c_2 = 0;
  int out = 0;
  float eta_1 = __VERIFIER_nondet_float();
  __SHADOWDP_v_epsilon = __SHADOWDP_v_epsilon + 0.500000000000000;
  float T_bar = T + eta_1;
  int c_1 = 0;
  int c_2 = 0;
  int i = 0;
  while ((c_1 < 1) && (i < size))
  {
    __VERIFIER_assert((c_1 < 1) && (i < size));
    float eta_2 = __VERIFIER_nondet_float();
    __VERIFIER_assume(__SHADOWDP_ALIGNED_DISTANCE_q[i] <= 1);
    __VERIFIER_assume(__SHADOWDP_ALIGNED_DISTANCE_q[i] >= -1);
    __VERIFIER_assume(__SHADOWDP_SHADOW_DISTANCE_q[i] == __SHADOWDP_ALIGNED_DISTANCE_q[i]);
    __SHADOWDP_v_epsilon = __SHADOWDP_v_epsilon + (((q[i] + eta_2) >= T_bar) ? (0.25 * Abs(__SHADOWDP_ALIGNED_DISTANCE_q[i] - 1)) : (0));
    if ((q[i] + eta_2) >= T_bar)
    {
      __VERIFIER_assume(__SHADOWDP_ALIGNED_DISTANCE_q[i] <= 1);
      __VERIFIER_assume(__SHADOWDP_ALIGNED_DISTANCE_q[i] >= -1);
      __VERIFIER_assume(__SHADOWDP_SHADOW_DISTANCE_q[i] == __SHADOWDP_ALIGNED_DISTANCE_q[i]);
      __VERIFIER_assert(((q[i] + __SHADOWDP_ALIGNED_DISTANCE_q[i]) + (eta_2 + (1 - __SHADOWDP_ALIGNED_DISTANCE_q[i]))) >= (T_bar + 1));
      __SHADOWDP_SHADOW_DISTANCE_out = (out + __SHADOWDP_SHADOW_DISTANCE_out) - ((q[i] + eta_2) - T_bar);
      out = (q[i] + eta_2) - T_bar;
      __SHADOWDP_SHADOW_DISTANCE_c_1 = (c_1 + __SHADOWDP_SHADOW_DISTANCE_c_1) - (c_1 + 1);
      c_1 = c_1 + 1;
    }
    else
    {
      __VERIFIER_assume(__SHADOWDP_ALIGNED_DISTANCE_q[i] <= 1);
      __VERIFIER_assume(__SHADOWDP_ALIGNED_DISTANCE_q[i] >= -1);
      __VERIFIER_assume(__SHADOWDP_SHADOW_DISTANCE_q[i] == __SHADOWDP_ALIGNED_DISTANCE_q[i]);
      __VERIFIER_assert(!((((q[i] + __SHADOWDP_ALIGNED_DISTANCE_q[i]) + eta_2) >= (T_bar + 1))));
      __SHADOWDP_SHADOW_DISTANCE_out = (out + __SHADOWDP_SHADOW_DISTANCE_out) - 0;
      out = 0;
      __SHADOWDP_SHADOW_DISTANCE_c_2 = (c_2 + __SHADOWDP_SHADOW_DISTANCE_c_2) - (c_2 + 1);
      c_2 = c_2 + 1;
    }

    if (((q[i] + __SHADOWDP_SHADOW_DISTANCE_q[i]) + eta_2) >= T_bar)
    {
      __SHADOWDP_SHADOW_DISTANCE_out = (((q[i] + __SHADOWDP_SHADOW_DISTANCE_q[i]) + eta_2) - T_bar) - out;
      __SHADOWDP_SHADOW_DISTANCE_c_1 = ((c_1 + __SHADOWDP_SHADOW_DISTANCE_c_1) + 1) - c_1;
    }
    else
    {
      __SHADOWDP_SHADOW_DISTANCE_out = 0 - out;
      __SHADOWDP_SHADOW_DISTANCE_c_2 = ((c_2 + __SHADOWDP_SHADOW_DISTANCE_c_2) + 1) - c_2;
    }

    i = i + 1;
  }

  __VERIFIER_assert(__SHADOWDP_v_epsilon <= 1);
  return out;
}

