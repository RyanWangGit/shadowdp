extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;


int diffsparsevector_2(float epsilon, int size, float q[], float T, float __LANG_distance_q[])
{
  __VERIFIER_assume(size > 0);
  float __LANG_v_epsilon = 0;

  float __LANG_distance_out = 0;
  float __LANG_distance_shadow_out = 0;
  int out = 0;
  float eta_1 = __VERIFIER_nondet_float();
  __LANG_v_epsilon = __LANG_v_epsilon + (0.5 * 1);
  float T_bar = T + eta_1;
  int c_1 = 0;
  int c_2 = 0;
  int i = 0;
  while ((c_1 < 1) && (i < size))
  {
    __VERIFIER_assert((c_1 < 1) && (i < size));
    float eta_2 = __VERIFIER_nondet_float();
    __VERIFIER_assume((__LANG_distance_q[i] >= -1) && (__LANG_distance_q[i] <= 1));
    __VERIFIER_assert(1 - __LANG_distance_q[i] <= 2);
    __LANG_v_epsilon = __LANG_v_epsilon + (((q[i] + eta_2) >= T_bar) ? (0.5 * 1) : (0));
    if ((q[i] + eta_2) >= T_bar)
    {
      __VERIFIER_assume((__LANG_distance_q[i] >= -1) && (__LANG_distance_q[i] <= 1));
      __VERIFIER_assert((q[i] + eta_2 + 1) >= (T_bar + 1));
      out = (q[i] + eta_2) - T_bar;
      c_1 = c_1 + 1;
      __LANG_distance_out = ((__LANG_distance_q[i] + 1) - __LANG_distance_q[i]) - 1;
      __LANG_distance_shadow_out = (__LANG_distance_q[i] + 0) - 0;
    }
    else
    {
      __VERIFIER_assume((__LANG_distance_q[i] >= -1) && (__LANG_distance_q[i] <= 1));
      __VERIFIER_assert(!(((q[i] + __LANG_distance_q[i]) + eta_2) >= (T_bar + 1)));
      out = 0;
      c_2 = c_2 + 1;
      __LANG_distance_out = 0;
      __LANG_distance_shadow_out = 0;
    }

    i = i + 1;
  }

  __VERIFIER_assert(__LANG_v_epsilon <= 1);
}
