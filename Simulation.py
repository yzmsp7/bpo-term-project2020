import numpy as np
import simpy


class Simulation:

    def __init__(self, arrival_rate=2, service_rate=3, servers=1, until=10):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.servers = servers
        self.until = until
        self.waiting_list = []
        self.records = []

    def generate_interarrival(self):
        return np.random.exponential(1. / self.arrival_rate)

    def generate_service(self):
        return np.random.exponential(1. / self.service_rate)

    def _drink_run(self, env, servers):
        cid = 0
        while True:
            cid += 1
            yield env.timeout(self.generate_interarrival())
            env.process(self._customer(env, cid, servers))

    def _customer(self, env, customer, servers):
        with servers.request() as request:
            t_arrival = env.now
            print('%.3f customer %d arrives' % (t_arrival, customer))
            yield request
            t_start = env.now
            print('%.3f customer %d is being served' % (t_start, customer))
            t_service = self.generate_service()
            yield env.timeout(t_service)
            t_depart = env.now
            print('%.3f customer %d departs' % (t_depart, customer))
            t_end = env.now
            self.waiting_list.append(t_depart - t_arrival)
            self.records.append({
                'customer': customer,
                'arriaval_time': t_arrival,
                'service': t_service,
                'start_time': t_start,
                'end_time': t_end,
                'waiting_time': t_start - t_arrival,
                'system_time': t_end - t_arrival,
                'served': servers.count,
            })

    def run_sim(self):
        np.random.seed(9487)
        env = simpy.Environment()
        servers = simpy.Resource(env, capacity=self.servers)
        env.process(self._drink_run(env, servers))
        env.run(until=10)

    def get_records(self) -> list:
        return self.records

