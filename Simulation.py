import numpy as np
import simpy

class Simulation:

    def __init__(self, arrival_rate=2, service_rate=3, servers=1, until=100):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.servers = servers
        self.until = until
        self.waiting_list = []
        self.records = []
        np.random.seed(9487)

    def _generate_interarrival(self):
        return -np.log(1-np.random.rand())/self.arrival_rate

    def _generate_service(self):
        return -np.log(1-np.random.rand())/self.service_rate

    def _drink_run(self, env, servers):
        cid = 0
        while True:
            cid += 1
            yield env.timeout(self._generate_interarrival())
            env.process(self._customer(env, cid, servers))

    def _customer(self, env, customer, servers):
        with servers.request() as request:
            t_arrival = env.now
            # print('%.3f customer %d arrives' % (t_arrival, customer))
            yield request
            t_start = env.now
            # print('%.3f customer %d is being served' % (t_start, customer))
            # choice = np.random.choice(np.arange(1, 3), p=[0.4, 0.6])
            t_service = self._generate_service()
            yield env.timeout(t_service)
            t_depart = env.now
            # print('%.3f customer %d departs' % (t_depart, customer))
            t_end = env.now
            self.waiting_list.append(t_depart - t_arrival)
            self.records.append({
                'customer': customer,
                'arrival_time': np.around(t_arrival, 3),
                'service': np.around(t_service, 3),
                'start_time': np.around(t_start, 3),
                'end_time': np.around(t_end, 3),
                'waiting_time': np.around(t_start - t_arrival, 3),
                'system_time': np.around(t_end - t_arrival, 3),
                'served_by': servers.count,
            })

    def run_sim(self):
        env = simpy.Environment()
        servers = simpy.Resource(env, capacity=self.servers)
        env.process(self._drink_run(env, servers))
        env.run(until=self.until)

    def get_records(self) -> list:
        return self.records

    def get_waiting(self) -> list:
        return self.waiting_list
