# Seedable pseudorandom number generator

## Usage

	var random = require('seedable-random');

	random.seed(123);
	console.log(random());

## As a `Math.random` replacement

	Math.random = require('seedable-random');
	Math.random.seed(12345);

- Works as a drop-in for `Math.random`

- Relatively fast (about 2.5 times slower than `Math.random` on my machine)

- Seeds itself from the clock by default

- Tries to be pretty random

- Well tested (TODO come up with some PRNG torture tests)

## TODO

Possibility to switch the generator (linear-feedback shift register, Mersenne
twister, digits of Math.sin(), etc. based on your needs)

## A word of warning

Current implementation just calls Math.sin() with the seed.  It's likely that
it's not quite that random (for example, the distribution could be biased
towards numbers near 1.0).  Some more tests are needed.

