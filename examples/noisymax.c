int noisymax (float epsilon, int size, float q[])
{
  int max = 0;
  int i = 0;
  float bq = 0;

  while(i < size)
  {
    float eta = Lap(2 / epsilon, "(q[i] + eta > bq || i == 0) ? SHADOW : ALIGNED; (q[i] + eta > bq || i == 0) ? ALIGNED : SHADOW; 2;");

    if(q[i] + eta > bq || i == 0)
    {
      max = i;
      bq = q[i] + eta;
    }
    i = i + 1;
  }
}
