---
title: How does Declo work?
---

## How does Declo work?
The goal of declo is to manipulate Python objects with JavaScript syntax. We can do using three strategies:

**Strategy 1:** 
Convert `js src => py src`. This can be kinda hard because of regex parsing etc, it will involve creating a custom grammar parser. This can be good at the start, but can quickly get complex, as and when we add more features. 


**Strategy 2:** 
Convert `js ast => py ast`. It is easier to work with structured data. Coding the rules for the equivalence is relatively easier.

**Strategy 3:** 
Convert `js src => py ast`. End to End convertion would be the best, but is the most complex which requires a mix of S1 and S2. 