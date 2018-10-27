extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern void __VERIFIER_assume(int);
extern int __VERIFIER_nondet_int();
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }

#define abs(x) ((x)<0 ? -(x) : (x))

typedef enum { false = 0, true = 1 } bool;

// change here to constant to test constant epsilon
#define EPSILON epsilon

int noisymax (float epsilon, int size, float q[]) {
  __VERIFIER_assume(epsilon > 0);
  __VERIFIER_assume(size > 0);
  float dq[size];
  for(int i = 0; i < size; i++)
    dq[i] = __VERIFIER_nondet_float();
  float v_epsilon = 0;

  int i = 0;
  float bq = 0, s_bq = 0, dis_bq = 0;
  float dis_s_bq = s_bq - bq;

  while(i < size)
  {
    float eta = __VERIFIER_nondet_float();
    float s_eta = eta; // maybe define dq[i] in latex
    __VERIFIER_assume(dq[i] <= 1 && -1 <= dq[i]);
    // align by 2
    v_epsilon = (q[i] + eta > bq || i == 0) ? EPSILON: v_epsilon;

    if(q[i] + eta > bq || i == 0)
    {
      __VERIFIER_assert(q[i] + dq[i] + eta + 2 > bq + dis_s_bq || i == 0);
      bq = q[i] + eta;
      dis_bq = dq[i] + 2;
    }
    else
    {
      __VERIFIER_assert(q[i] + dq[i] + eta <= bq + dis_bq);
    }

    // shadow execution
    s_bq = bq + dis_s_bq;
    if(q[i] + dq[i] + s_eta > s_bq || i == 0)
    {
      s_bq = q[i] + dq[i] + s_eta;
      dis_s_bq = s_bq - bq;
    }
    i = i + 1;
  }
  __VERIFIER_assert(v_epsilon <= EPSILON);
}
