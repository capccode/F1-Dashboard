var seed = new Date().getTime();

function random() {
	// Avoid repeating when seeded by a number larger than the maximum integer
	// representable in JavaScript (2^53).  
	if (seed >= 9007199254740992) {
		seed = 0;
	}
	var x = Math.sin(.8765111159592828 + seed++) * 10000.0;
	return x - Math.floor(x);
}

random.seed = function(newSeed) {
	seed = newSeed;
}

module.exports = random;

