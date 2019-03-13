void smartsum(float epsilon, int size, float q[], float T, int M)
{
  "ONE_DIFFER";
  float out = 0;
  float next = 0; float n = 0; int i = 0; float sum = 0;
  while(i <= T && i < size)
  {
    if ((i + 1) % M == 0)
    {
      float eta_1 = Lap(1.0 / epsilon, "ALIGNED; __LANG_ALIGNED_sum - sum + __LANG_ALIGNED_q[i] - q[i];");
      n = n + sum + q[i] + eta_1;
      next = n;
      sum = 0;
      out = next;
    }
    else
    {
      float eta_2 = Lap(1.0 / epsilon, "ALIGNED; __LANG_ALIGNED_sum - sum;");
      next = next + q[i] + eta_2;
      sum = sum + q[i];
      out = next;
    }
    i = i + 1;
  }
  return out;
}