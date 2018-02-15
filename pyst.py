import inspect, os, importlib, re
currtestr = []
class TestCase:
    def assertEquals(self, a, b):
        lineno = inspect.currentframe().f_back.f_lineno
        if a == b:
            self.add_result(0, lineno);  # Everything OK
        else:
            self.add_result(1, lineno);  # This is not equal

    def assertSame(self, a, b):
        lineno = inspect.currentframe().f_back.f_lineno
        if a is b:
            self.add_result(0, lineno);  # Everything OK
        else:
            self.add_result(1, lineno);  # This is not equal

    def assertMore(self, a, b):
        lineno = inspect.currentframe().f_back.f_lineno
        if a > b:
            self.add_result(0, lineno);  # Everything OK
        else:
            self.add_result(1, lineno);  # This is not equal

    def assertLess(self, a, b):
        lineno = inspect.currentframe().f_back.f_lineno
        if a < b:
            self.add_result(0, lineno);  # Everything OK
        else:
            self.add_result(1, lineno);  # This is not equal

    def assertNone(self, a):
        lineno = inspect.currentframe().f_back.f_lineno
        if a is None:
            self.add_result(0, lineno);  # Everything OK
        else:
            self.add_result(1, lineno);  # This is not equal

    def add_result(self, r, ln):
        currtestr.append((r, ln))

def decor_results(r):
    res = []
    for result in r:
        if result[0] == 0:
            res.append('OK')
        else:
            res.append('Failed')
    return res

def get_lines_around(filename, lineno):
    flines = open(filename, mode='r').readlines()
    padding = 5
    # Decorate it
    r0 = ''
    r1 = ' '*(padding-len('>' + str(lineno)))+'>'+str(lineno)+('|' + flines[lineno-1])
    r2 = ''
    if lineno < len(flines) and lineno == 1:
        r2 = ' '*(padding-len(str(lineno+1)))+str(lineno+1)+('|' + flines[lineno])
    elif lineno == len(flines) and lineno > 1:
        r0 = ' '*(padding-len(str(lineno-1)))+str(lineno-1)+('|' + flines[lineno-2])
    else:
        r2 = ' '*(padding-len(str(lineno+1)))+str(lineno+1)+('|' + flines[lineno])
        r0 = ' '*(padding-len(str(lineno-1)))+str(lineno-1)+('|' + flines[lineno-2])
    return r0 + r1 + r2

def r_contains(r, w):
    res = False
    for c in r:
        if c[0] == w:
            res = True
            break
    return res

def removentests(l, f=True):
    i = 0
    while i < len(l):
        if f:
            if not l[i].startswith('test_'):
                l.remove(l[i])
            else:
                i+=1
        else:
            if not l[i][0].startswith('test_'):
                l.remove(l[i])
            else:
                i+=1
    return l

def test_cases(a):
    test_caser = []
    tests_run = 0
    ok = True
    if isinstance(a, TestCase) or issubclass(a, TestCase):
        if inspect.isclass(a):
            a = a()
        methods = inspect.getmembers(a, predicate=inspect.ismethod)
        for tmethod in methods:
            if tmethod[0].startswith('test_'):
                tests_run += 1
                getattr(a, tmethod[0])()
                #print("Result for " + tmethod[0] + " in " + a.__class__.__name__ + ": " + str(decor_results(currtestr)))
                test_caser.append(currtestr.copy())
                if r_contains(currtestr, 1):
                    ok = False
                currtestr.clear()
    else:
        raise TypeError
    return (tests_run, ok, test_caser)

def main():
    # Get testcases
    tests = os.listdir()
    i = 0
    # print(tests)
    # while i < len(tests):
    #     if not tests[i].startswith('test_'):
    #         tests.remove(tests[i])
    #     else:
    #         i+=1
    tests = removentests(tests)
    # print(tests)
    modules = []
    for testf in tests:
        modules.append(importlib.import_module(inspect.getmodulename(testf)))
    # print(modules)
    testcases = []
    for module in modules:
        for testcase in inspect.getmembers(module, predicate=inspect.isclass):
            testcases.append(testcase[1])

    # Run testcases
    testcases_run = 0
    testcasesr = []
    tests_run = 0
    succeded = True
    for testcase in testcases:
        testcases_run += 1
        t = test_cases(testcase)
        fname = inspect.getfile(testcase)
        for test in t[2]:
            for assertion in test:
                failed = assertion[0] == 1
                lineno = assertion[1]
                if failed:
                    methodtests = removentests(inspect.getmembers(testcase(), predicate=inspect.ismethod), f=False)
                    method = methodtests[t[2].index(test)]
                    #print(method)
                    print('Failed in', method[0], 'in', testcase.__name__)
                    print(get_lines_around(fname, lineno))
        tests_run += t[0]
        testcasesr.append(t[2])
        if t[1] == False:
            succeded = False
            break
    tstr = 'tests'
    if tests_run == 1:
        tstr = 'test'
    tcstr = 'testcases'
    if testcases_run == 1:
        tcstr = 'testcase'
    print('Ran ' + str(tests_run) + ' ' + tstr + ' in ' + str(testcases_run), tcstr)
    if succeded:
        print('OK')
    else:
        print('Failed')

if __name__ == '__main__':
    main()
