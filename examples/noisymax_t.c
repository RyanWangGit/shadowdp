extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;
    
int noisymax(float epsilon, int size, float q[])
{
  __VERIFIER_assume(epsilon >= 0);
  float __LANG_v_epsilon = 0;
  float __LANG_distance_q[size];
  for (int __LANG_i = 0; __LANG_i < size; __LANG_i++)
    __LANG_distance_q[__LANG_i] = __VERIFIER_nondet_float();

  float __LANG_distance_bq = 0;
  float __LANG_distance_shadow_bq = 0;
  int max = 0;
  int i = 0;
  float bq = 0;
  while (i < size)
  {
    __VERIFIER_assert(i < size);
    float eta = __VERIFIER_nondet_float();
    __LANG_v_epsilon = (((q[i] + eta) > bq) || (i == 0)) ? (0 + epsilon) : (__LANG_v_epsilon + 0);
    if (((q[i] + eta) > bq) || (i == 0))
    {
      __VERIFIER_assume((__LANG_distance_q[i] >= -1) && (__LANG_distance_q[i] <= 1));
      __VERIFIER_assert((((q[i] + __LANG_distance_q[i]) + (eta + 2)) > (bq + __LANG_distance_shadow_bq)) || (i == 0));
      max = i;
      bq = q[i] + eta;
      __LANG_distance_bq = __LANG_distance_q[i] + 2;
    }
    else
    {
      __VERIFIER_assume((__LANG_distance_q[i] >= -1) && (__LANG_distance_q[i] <= 1));
      __VERIFIER_assert(!((((q[i] + __LANG_distance_q[i]) + eta) > (bq + __LANG_distance_bq)) || (i == 0)));
      __LANG_distance_bq = __LANG_distance_bq;
    }

    if ((((q[i] + __LANG_distance_q[i]) + eta) > (bq + __LANG_distance_shadow_bq)) || (i == 0))
    {
      __LANG_distance_shadow_bq = __LANG_distance_q[i] + 0;
    }

    i = i + 1;
  }

  __VERIFIER_assert(__LANG_v_epsilon <= epsilon);
}

