-->
500
     if values["n"] < 1:   
501
         raise ValueError("n must be at least 1.")   
502
     if values["n"] > 1 and values["streaming"]: KeyError: 'n'
