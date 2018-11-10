extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;
    
void smartsum(float epsilon, int size, float q[], float T, float M)
{
  __VERIFIER_assume(epsilon >= 0);
  float __LANG_v_epsilon = 0;
  float __LANG_distance_q[size];
  for (int __LANG_i = 0; __LANG_i < size; __LANG_i++)
    __LANG_distance_q[__LANG_i] = __VERIFIER_nondet_float();

  float __LANG_distance_out = 0;
  float __LANG_distance_shadow_out = 0;
  float __LANG_distance_next = 0;
  float __LANG_distance_shadow_next = 0;
  float __LANG_distance_n = 0;
  float __LANG_distance_shadow_n = 0;
  float __LANG_distance_sum = 0;
  float __LANG_distance_shadow_sum = 0;
  float out = 0;
  float next = 0;
  float n = 0;
  int i = 0;
  float sum = 0;
  while (i <= T)
  {
    __VERIFIER_assert(i <= T);
    if (((i + 1) % M) == 0)
    {
      __VERIFIER_assert(((i + 1) % M) == 0);
      float eta_1 = __VERIFIER_nondet_float();
      __LANG_v_epsilon = __LANG_v_epsilon + (__LANG_distance_sum + (__LANG_distance_q[i] * (1 / (1.0 / epsilon))));
      n = ((n + sum) + q[i]) + eta_1;
      next = n;
      sum = 0;
      out = next;
      __LANG_distance_out = (((__LANG_distance_n + __LANG_distance_sum) + __LANG_distance_q[i]) + __LANG_distance_sum) + __LANG_distance_q[i];
      __LANG_distance_next = (((__LANG_distance_n + __LANG_distance_sum) + __LANG_distance_q[i]) + __LANG_distance_sum) + __LANG_distance_q[i];
      __LANG_distance_n = (((__LANG_distance_n + __LANG_distance_sum) + __LANG_distance_q[i]) + __LANG_distance_sum) + __LANG_distance_q[i];
      __LANG_distance_sum = 0;
      __LANG_distance_shadow_n = ((__LANG_distance_shadow_n + __LANG_distance_shadow_sum) + __LANG_distance_q[i]) + 0;
      __LANG_distance_shadow_next = __LANG_distance_shadow_n;
      __LANG_distance_shadow_sum = 0;
      __LANG_distance_shadow_out = __LANG_distance_shadow_next;
    }
    else
    {
      __VERIFIER_assert(!(((i + 1) % M) == 0));
      float eta_2 = __VERIFIER_nondet_float();
      __LANG_v_epsilon = __LANG_v_epsilon + ((1.0 * __LANG_distance_sum) * epsilon);
      next = (next + q[i]) + eta_2;
      sum = sum + q[i];
      out = next;
      __LANG_distance_out = (__LANG_distance_next + __LANG_distance_q[i]) + __LANG_distance_sum;
      __LANG_distance_next = (__LANG_distance_next + __LANG_distance_q[i]) + __LANG_distance_sum;
      __LANG_distance_n = __LANG_distance_n;
      __LANG_distance_sum = __LANG_distance_sum + __LANG_distance_q[i];
      __LANG_distance_shadow_next = (__LANG_distance_shadow_next + __LANG_distance_q[i]) + 0;
      __LANG_distance_shadow_sum = __LANG_distance_shadow_sum + __LANG_distance_q[i];
      __LANG_distance_shadow_out = __LANG_distance_shadow_next;
    }
    i = i + 1;
  }

  __VERIFIER_assert(__LANG_v_epsilon <= epsilon);
}

