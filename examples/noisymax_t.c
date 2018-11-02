extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern void __VERIFIER_assume(int);
extern int __VERIFIER_nondet_int();
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }

#define abs(x) ((x)<0 ? -(x) : (x))

typedef enum { false = 0, true = 1 } bool;


int noisymax (float epsilon, int size, float q[]) {
  __VERIFIER_assume(epsilon >= 0);
  float __LANG_distance_q[size];
  for(int i = 0; i < size; i++)
    __LANG_distance_q[i] = __VERIFIER_nondet_float();
  float __LANG_v_epsilon = 0;
  int max; float __LANG_distance_max; float __LANG_distance_shadow_max;

  int i = 0;
  float bq = 0; float __LANG_distance_bq = 0; float __LANG_distance_shadow_bq = 0;

  __LANG_distance_bq = 0;
  while(i < size)
  {
    float eta = __VERIFIER_nondet_float();
    // align by 2
    __LANG_v_epsilon = (q[i] + eta > bq || i == 0) ? 0 +  2 * (epsilon / 2.0): __LANG_v_epsilon + 0;

    if(q[i] + eta > bq || i == 0)
    {
      __VERIFIER_assume(__LANG_distance_q[i] <= 1 && -1 <= __LANG_distance_q[i]);
      __VERIFIER_assert(q[i] + __LANG_distance_q[i] + eta + 2 > bq + __LANG_distance_shadow_bq || i == 0);
      bq = q[i] + eta;
      __LANG_distance_bq = __LANG_distance_q[i] + 2;
    }
    else
    {
      __VERIFIER_assume(__LANG_distance_q[i] <= 1 && -1 <= __LANG_distance_q[i]);
      __VERIFIER_assert(!(q[i] + __LANG_distance_q[i] + eta + 0 > bq + __LANG_distance_bq || i == 0));
    }

    // shadow execution
    if(q[i] + __LANG_distance_q[i] + eta + 0 > bq + __LANG_distance_shadow_bq || i == 0)
    {
      __LANG_distance_shadow_max = i - max;
      __LANG_distance_shadow_bq = __LANG_distance_q[i] + 0;
    }
    i = i + 1;
  }
  __VERIFIER_assert(__LANG_v_epsilon <= epsilon);
}
