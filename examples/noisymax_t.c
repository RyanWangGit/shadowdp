/* Implementation of sparse vector
 */
extern void __VERIFIER_error() __attribute__ ((__noreturn__));
extern int __VERIFIER_nondet_float(void);
extern void __VERIFIER_assume(int);
extern int __VERIFIER_nondet_int();
extern void __assert_fail();
#define __VERIFIER_assert(cond) { if(!(cond)) { __assert_fail(); } }

#define abs(x) ((x)<0 ? -(x) : (x))

typedef enum { false = 0, true = 1 } bool;

#define SIZE 4

int noisymax (float epsilon, float q[]) {

  __VERIFIER_assume(epsilon > 0);

  int i = 0, bq = 0, s_bq = 0, dis_bq=0;
  int dis_s_bq = s_bq - bq;
  float v_epsilon = 0;

  while(i < SIZE)
  {
    float dis_q = __VERIFIER_nondet_float();
    __VERIFIER_assume(dis_q >= -1 && dis_q <= 1);
    float eta = __VERIFIER_nondet_float();
    float s_eta = eta;
    v_epsilon = ((q[i] + eta > bq || i = 0) ? (abs(1 - dis_q) * (epsilon / 2.0)) : v_epsilon);

    if(q[i] + eta > bq || i = 0)
    {
      __VERIFIER_assert(q[i] + eta + 1 > bq + dis_s_bq || i = 0);
      int max = i;
      bq = q[i] + eta;
      dis_bq = 1;
    }
    else
    {
      __VERIFIER_assert(!(q[i] + dis_q + eta > bq + dis_bq || i = 0));
    }

    // shadow execution
    if(q[i] + dis_q + s_eta > s_bq || i = 0)
    {
      int s_max = i;
      s_bq = q[i] + dis_q + s_eta;
      dis_s_bq = s_bq - bq;
    }
    i = i + 1;
  }
}

bool is_bounded(float *arr, int size)
{
  bool res = true;
  for(int i = 0; i < size; i ++)
    res = res & (arr[i] >= -1 && arr[i] <= 1);
  return res;
}

int main() {
  float a[SIZE];
  float da[SIZE];

  unsigned int i;
  for(i = 0; i < SIZE; i++)
    a[i] = __VERIFIER_nondet_float();

  //for(i = 0; i < SIZE; i++)
  {
    //da[i] = __VERIFIER_nondet_float();
    //__VERIFIER_assume(da[i] >= -1 && da[i] <= 1);
  }



  float epsilon = __VERIFIER_nondet_float();

  return noisymax(epsilon, a);
}
