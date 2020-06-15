# shor
An implementation of Shor's factoring algorithm for the CS269Q final project at Stanford.

To run the algorithm, you'll need to have the latest versions of Pyquil and Numpy. Additionally, you need to use Python >= 3.6, due to the constraints of Pyquil.
```
pip install numpy
pip install pyquil
```
Next, install the Rigetti QVM from the [Rigetti website](https://www.rigetti.com/forest).

Once you've gotten everything set up, run the QVM server with the following command:
```
qvm -S
```

Now, you're ready to run Shor's algorithm. To do so, use the following command, where N is the number you want to factor.
```
python shor.py N
```
