int noisymax (float epsilon, int size, float q[])
{
  int i = 0;
  float bq = 0;

  while(i < size)
  {
    float eta = Lap(2 / epsilon, "S_e = q[i] + eta > bq || i == 0 ? SHADOW : ALIGNED; S_eta = q[i] + eta > bq || i == 0 ? ALIGNED : SHADOW; eta : 1");

    if(q[i] + eta > bq || i == 0)
    {
      int max = i;
      bq = q[i] + eta;
    }
    i = i + 1;
  }
}
