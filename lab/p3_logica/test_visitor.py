import agentspeak.runtime as runtime
import agentspeak.stdlib
import agentspeak
import tempfile, os

def try_parse(name, code):
    with tempfile.NamedTemporaryFile(suffix='.asl', mode='w', delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        env = runtime.Environment()
        with open(fname) as f:
            env.build_agent(f, agentspeak.stdlib.actions)
        print('OK:', name)
    except Exception as e:
        print('FAIL [' + name + ']:', str(e)[:120])
    finally:
        os.unlink(fname)

try_parse('member_state_with_list',
    'r(X,V) :- not .member(state(X, left), V).\n+!s <- true.\n')

try_parse('inline_solve_state_with_list',
    'solve(C,V) :- move(C, state(Pos, T, E), A) & not .member(state(Pos,T), V).\n+!s <- true.\n')
