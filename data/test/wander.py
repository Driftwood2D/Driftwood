import random

def init(ent):
    def schedule_wander():
        delay = random.randrange(500, 750)
        Driftwood.log.info("Wander", "schedule_wander", "delay={}".format(delay))
        Driftwood.tick.register(tick, delay=delay, once=True)

    def tick(millis_past):
        x = 0
        y = 0
        if random.choice(('x', 'y')) == 'x':
            x = random.choice((-1, 0, 0, 0, 1))
        else:
            y = random.choice((-1, 0, 0, 0, 1))
        Driftwood.log.info("Wander", "tick", "x={} y={}".format(x, y))
        ent.set_next_velocity(x, y)
        schedule_wander()

    schedule_wander()
