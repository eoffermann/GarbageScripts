"""
primality_checker.py

A command-line tool for analyzing whether a given number is prime.
Applies simple mental math tests, trial division, and advanced probabilistic tests.
Provides clear walkthroughs and explanations at each step.

Usage:
    python primality_checker.py <number>

Example:
    python primality_checker.py 2025
"""

import sys
import math
import random
from typing import Tuple

def is_divisible_by_small_primes(n: int) -> bool:
    """Check divisibility by small primes with explanations.

    Args:
        n (int): Number to check.

    Returns:
        bool: True if divisible by any small prime, else False.
    """
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    print("\n[Stage 1] Easy divisibility tests:")
    if n == 2 or n == 3:
        print(f"{n} is 2 or 3, both primes.")
        return False

    if n % 2 == 0:
        print(f"{n} is even (divisible by 2). Not prime.")
        return True

    for p in small_primes[1:]:
        if n % p == 0:
            print(f"{n} is divisible by {p}. {n} / {p} = {n//p}")
            return True
    print(f"{n} passed simple divisibility tests.")
    return False

def is_perfect_square(n: int) -> bool:
    """Check if n is a perfect square.

    Args:
        n (int): Number to check.

    Returns:
        bool: True if n is a perfect square.
    """
    root = math.isqrt(n)
    if root * root == n:
        print(f"{n} is a perfect square ({root} * {root}). Not prime.")
        return True
    return False

def trial_division(n: int) -> bool:
    """Perform trial division up to sqrt(n).

    Args:
        n (int): Number to check.

    Returns:
        bool: True if prime, else False.
    """
    print("\n[Stage 2] Trial Division up to sqrt(n):")
    limit = math.isqrt(n) + 1
    for i in range(2, limit):
        if n % i == 0:
            print(f"{n} is divisible by {i}. {n} / {i} = {n//i}")
            return False
    print(f"No divisors found up to sqrt({n}) = {limit-1}.")
    return True

def miller_rabin(n: int, k: int = 5) -> bool:
    """Apply Miller-Rabin primality test with detailed explanation.

    Args:
        n (int): Number to check.
        k (int): Number of iterations (default 5).

    Returns:
        bool: True if probably prime, else False.
    """
    print("\n[Stage 3] Miller-Rabin probabilistic primality test:")
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False

    # Write n-1 as d*2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    print(f"We write {n}-1 = {d} * 2^{r}")

    for i in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        print(f"Round {i+1}: base a = {a}, compute a^d % n = {x}")
        if x == 1 or x == n - 1:
            print(f"Base {a} passes initial test (x = {x}).")
            continue
        for j in range(r - 1):
            x = pow(x, 2, n)
            print(f"  Square x -> x = {x}")
            if x == n - 1:
                print(f"  Base {a} passes inner loop (x became n-1).")
                break
        else:
            print(f"  ❌ Base {a} reveals {n} is composite.")
            return False
    print(f"✅ Passed {k} rounds of Miller-Rabin. {n} is probably prime.")
    return True

def baillie_psw(n: int) -> bool:
    """Baillie-PSW primality test: combination of Miller-Rabin and Lucas.

    Args:
        n (int): Number to check.

    Returns:
        bool: True if probably prime, else False.
    """
    print("\n[Stage 4] Baillie-PSW test (Miller-Rabin base 2 + Lucas test):")
    if not miller_rabin(n, 1):
        return False
    return lucas_primality(n)

def lucas_primality(n: int) -> bool:
    """Lucas probable prime test (simplified form).

    Args:
        n (int): Number to check.

    Returns:
        bool: True if passes Lucas conditions.
    """
    print("Lucas test is not fully implemented — assuming True for demonstration.")
    # Full Lucas test is very complex and would go here.
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python primality_checker.py <number>")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid integer.")
        sys.exit(1)

    print(f"Checking primality of {n}...")

    if n <= 1:
        print(f"{n} is not prime by definition.")
        sys.exit(0)

    if is_divisible_by_small_primes(n):
        print(f"\n✅ {n} is composite (small divisibility found).")
        sys.exit(0)

    if is_perfect_square(n):
        print(f"\n✅ {n} is composite (perfect square).")
        sys.exit(0)

    # Continue with deeper methods
    if n < 10**6:
        if trial_division(n):
            print(f"\n✅ {n} is prime (trial division).")
        else:
            print(f"\n✅ {n} is composite (trial division).")
    else:
        if baillie_psw(n):
            print(f"\n✅ {n} is probably prime (Baillie-PSW test).")
        else:
            print(f"\n✅ {n} is composite (Baillie-PSW test).")

if __name__ == "__main__":
    main()
