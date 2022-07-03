class BinComb:
  def __init__(self, keywords):
    self.keywords = keywords
    self.comb     = len(self.keywords)

  def get_combinations(self):
    num1 = '0' * self.comb
    sum  = num1
    num2 = '1'

    couples  = {}

    for i in range(1, len(self.keywords)+1):
      couples[i]=[]

    for i in range(0, 2**self.comb-1):
      sum = bin(int(sum, 2) + int(num2, 2))
      output = (len(num1)-len(sum[2:]))*'0' + sum[2:]
      couples[output.count('1')].append(output)

    to_output = []
    for key in couples.keys():
      figures = couples[key]
      outer_or_output = []
      for fig in figures:
        inner_and_output = []
        for bit in range(0, len(fig)):
          calc = self.keywords[bit] * int(fig[bit])
          if len(calc) > 0:
            inner_and_output.append(self.keywords[bit] * int(fig[bit]))
        outer_or_output.append("&".join(inner_and_output))
      to_output.append("|".join(outer_or_output))
    to_output.reverse()
    return to_output
