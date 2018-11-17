extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern int __VERIFIER_nondet_int();
extern void __VERIFIER_assume(int);
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }
#define abs(x) ((x) < 0 ? -(x) : (x))
typedef enum { false = 0, true = 1 } bool;

void smartsum(float epsilon, int size, float q[], float T, int M, float __LANG_distance_q[], int __LANG_index)
{
  __VERIFIER_assume(size > 0);
  __VERIFIER_assume(T < size && T > 0);
  __VERIFIER_assume(M > 0 && M < size);
  __VERIFIER_assume(__LANG_index > 0 && __LANG_index < size);

  float __LANG_v_epsilon = 0;

  float __LANG_distance_out = 0;
  float __LANG_distance_next = 0;
  float __LANG_distance_n = 0;
  float __LANG_distance_sum = 0;
  float out = 0;
  float next = 0;
  float n = 0;
  int i = 0;
  float sum = 0;
  while (i <= T && i < size)
  {
    __VERIFIER_assert(i <= T && i < size);

    if (((i + 1) % M) == 0)
    {
      __VERIFIER_assert(((i + 1) % M) == 0);
      float eta_1 = __VERIFIER_nondet_float();
      if (i == __LANG_index)
      {
        __VERIFIER_assume(__LANG_distance_q[i] <= 1 && __LANG_distance_q[i] >= -1);
        __LANG_v_epsilon = __LANG_v_epsilon + abs(__LANG_distance_sum + __LANG_distance_q[i]);
      }
      else
      {
        __VERIFIER_assume(__LANG_distance_q[i] == 0);
        __LANG_v_epsilon = __LANG_v_epsilon + __LANG_distance_sum;

      }
      n = ((n + sum) + q[i]) + eta_1;
      next = n;
      sum = 0;
      out = next;
       __LANG_distance_n = __LANG_distance_n;
       __LANG_distance_next = __LANG_distance_n;
        __LANG_distance_sum = 0;
      __LANG_distance_out = __LANG_distance_n;
    }
    else
    {
      __VERIFIER_assert(!(((i + 1) % M) == 0));
      float eta_2 = __VERIFIER_nondet_float();
      if (i == __LANG_index)
      {
        __VERIFIER_assume(__LANG_distance_q[i] <= 1 && __LANG_distance_q[i] >= -1);
        __LANG_v_epsilon = __LANG_v_epsilon + abs(__LANG_distance_q[i]);
      }
      else
      {
        __VERIFIER_assume(__LANG_distance_q[i] == 0);
        __LANG_v_epsilon = __LANG_v_epsilon + __LANG_distance_q[i];
      }
      next = (next + q[i]) + eta_2;
      sum = sum + q[i];
      out = next;
      __LANG_distance_next = __LANG_distance_next;
       __LANG_distance_sum = __LANG_distance_sum + abs(__LANG_distance_q[i]);
      __LANG_distance_out = __LANG_distance_next;
      __LANG_distance_n = __LANG_distance_n;
    }
    i = i + 1;
  }

  __VERIFIER_assert(__LANG_v_epsilon <= 2);
}
