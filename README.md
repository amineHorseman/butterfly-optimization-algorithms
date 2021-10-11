# Butterfly Optimization Algorithm(s)

Implementation the Butterfly Optimization Algorithm and some of its variants
1. **BOA**: The standard BOA algorithm from [Arora et al. 2019] & [Arora et al. 2016]
2. **mBOA**: BOA with intensive search from [Arora et al. 2018]
3. **ABOA**: BOA with a non-linear update rule for the sensory modality from [Zhang et al. 2020]
4. **SABOA**: BOA with Self-Adaptative update rule from [Fan et al. 2020]
5. **xBOA**: BOA with crossover operator from [Bendahmane et al. 2021]



## Dependencies

Please install the following packages to use this repository
```
pip install numpy
pip install pyyaml
pip install pygmo
```


## How to use

1. Change the parameters in the file `params.yaml`

   - A description of each parameter is given as a comment in the .yaml file
   - You can remove a parameter by commenting or removing its line, it will be replaced by the default value automatically

2. Launch the main script
   ```
   python main.py
   ```
3. You will get an output similar to this:
   ```
   Solving problem using xBOA: Crossover Butterfly Optimization Algorithm (UDA)
     Gen    Fevals     Fbest       Improv     Duration
      1       11    900.098353  -10.484016      0.0
      2       16    585.152347  -314.946006     0.0
      3       21    331.047822  -254.104524     0.0
      4       26    177.079935  -153.967888     0.0
      5       32    147.851095   -29.228839     0.0
      6       39    147.851095     0.0          0.0
      7       44     71.580096   -76.270999     0.0
      8       49     42.675169   -28.904927     0.0
      9       55     35.876333    -6.798837     0.0
      10      61     19.645902   -16.23043      0.0
   Executed: 10 generations
   Best solution: [ 0.12479103  0.08723433  0.          0.44437604  0.17309622  0. 0.25159349  0.32912562  3.50034695  0.          0.         11.41293089 1.46827132  0.          0.          0.29118183  0.          1.56295445 0.          0. ]
   ```



## How to cite
...




## Contribute

Contributions are welcome. You may help with the following:
- Writing documentation & turorials
- Adding new algorithms
- Improving code & performances
- Writing automated tests
- Debugging
- Translation

Please open a new issue for each contribution before sending a pull request.

## References

- Arora S, Singh S (2016) *"An improved butterfly
optimization algorithm for global optimization"*.
Advanced Science, Engineering and Medicine
8(9):711–717
- Arora S, Singh S, Yetilmezsoy K (2018) *"A
modified butterfly optimization algorithm for mechanical design optimization problems"*. Journal of the Brazilian Society of Mechanical Sciences and Engineering 40(1):1–17
- Arora S, Singh S (2019) *"Butterfly optimization
algorithm: a novel approach for global optimization"*. Soft Computing 23(3):715–734
- Bendahmane et al. 2021: Paper under review (details to be added later)
- Fan Y, Shao J, Sun G, et al (2020) *"A self-adaption
butterfly optimization algorithm for numerical optimization problems"*. IEEE Access 8:88,026–88,041
- Zhang M, Long D, Qin T, et al (2020) *"A
chaotic hybrid butterfly optimization algorithm
with particle swarm optimization for highdimensional optimization problems"*. Symmetry
12(11):1800
