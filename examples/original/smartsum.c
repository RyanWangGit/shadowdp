void smartsum(float epsilon, int size, float q[], float T, float M)
{
  float out = 0;
  float next = 0; float n = 0; int i = 0; float sum = 0;
  while(i <= T && i < size)
  {
    if ((i + 1) % M == 0)
    {
      float eta_1 = Lap(1.0 / epsilon, "ALIGNED; ALIGNED; __LANG_distance_sum + __LANG_distance_q[i]");
      n = n + sum + q[i] + eta_1;
      next = n;
      sum = 0;
      out = next;
    }
    else
    {
      float eta_2 = Lap(1.0 / epsilon, "ALIGNED; ALIGNED; __LANG_distance_sum");
      next = next + q[i] + eta_2;
      sum = sum + q[i];
      out = next;
    }
    i = i + 1;
  }
}