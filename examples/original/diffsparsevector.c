int diffsparsevector(float epsilon, int size, float q[], float T)
{
  "ALL_DIFFER";
  int out = 0;
  float eta_1 = Lap(2.0 / epsilon, "ALIGNED; 1");
  float T_bar = T + eta_1;
  int c_1 = 0, c_2 = 0;
  int i = 0;

  while (c_1 < 1 && i < size)
  {
    float eta_2 = Lap((4.0 * 1) / epsilon, "ALIGNED; (q[i] + eta_2 >= T_bar) ? (1 - (__LANG_ALIGNED_q[i] - q[i])) : 0;");

    if (q[i] + eta_2 >= T_bar)
    {
      out = q[i] + eta_2 - T_bar;
      c_1 = c_1 + 1;
    }
    else
    {
      out = 0;
      c_2 = c_2 + 1;
    }
    i = i + 1;
  }
  return out;
}
