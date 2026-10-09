def feedback(code, guess):

    # calculate exact matches
    exact = sum(a == b for a, b in zip(code, guess))
    
    # calculate partial matches by tracking remaining unmatched symbols
    code_remain = [c for c, g in zip(code, guess) if c != g]
    guess_remain = [g for c, g in zip(code, guess) if c != g]
    
    partial = 0
    for g in guess_remain:
        if g in code_remain:
            partial += 1
            code_remain.remove(g)
            
    return exact, partial
