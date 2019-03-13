int partialsum (float epsilon, int size, float q[])
{
  "ONE_DIFFER";
  float out = 0;
  float sum = 0; int i = 0;
  while(i < size)
  {
    sum = sum + q[i];
    i = i + 1;
  }
  float eta = Lap(1.0 / epsilon, "ALIGNED; __LANG_ALIGNED_sum - sum;");
  out = sum + eta;
  return out;
}
