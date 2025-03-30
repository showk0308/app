# sample
# def test_a():
#     assert 6 == multiplication(2, 3)

# def multiplication(x, y):
#     return x * y

def test_conditions():
    #aperture = 40  # 現在の開度

    assert 40 == condition_judgement(29, 40)
    assert 60 == condition_judgement(30, 40)
    assert 50 == condition_judgement(31, 40)
    assert 50 == condition_judgement(33, 40)
    assert 20 == condition_judgement(34, 40)
    assert 20 == condition_judgement(35, 40)
    assert 0 == condition_judgement(36, 40)

def condition_judgement(now_degree: int, now_aperture: int) -> int:
    aperture = -1
    prev_degree = -273
    prev_aperture = now_aperture  # 現在の開度

    degrees     =   [30, 33, 35]  
    apertures   =   [60, 50, 20]

    min_degree = min(degrees)
    max_degree = max(degrees)
    
    if now_degree < min_degree:
        return prev_aperture
    elif now_degree > max_degree:
        return 0;

    for digree, aptr in zip(degrees, apertures):
        print(f'now_degree:{now_degree} dgr:{digree} aptr:{aptr} prev_degree:{prev_degree} prev_aperture:{prev_aperture}')
        if now_degree < prev_degree:
            aperture = prev_aperture
            break
        elif prev_degree < now_degree <= digree:
            aperture = aptr
            break
        elif now_degree > digree:
            prev_degree = digree
            prev_aperture = aptr
        else:
            break

    if aperture == -1:
        aperture = 0
    
    return aperture
