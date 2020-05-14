import numpy as np
import simpy
import datetime as dt


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
        # rate /hr
        return -np.log(1-np.random.rand())/self.arrival_rate

    def _generate_service(self):
        # rate /hr
        return -np.log(1-np.random.rand())/self.service_rate

    def _drink_run(self, env, servers):
        cid = 0
        while True:
            cid += 1
            yield env.timeout(self._generate_interarrival())
            env.process(self._customer(env, cid, servers))

    def _customer(self, env, customer, servers):
        t = dt.datetime(2020, 5, 14, 10, 30, 0)  # start from 10:30 a.m.
        with servers.request() as request:
            t_arrival = np.around(env.now, 3)
            t_arrival = t + dt.timedelta(minutes=t_arrival*60)
            # print('%.3f customer %d arrives' % (t_arrival, customer))
            yield request
            t_start = np.around(env.now, 3)
            t_start = t + dt.timedelta(minutes=t_start*60)

            # print('%.3f customer %d is being served' % (t_start, customer))
            # choice = np.random.choice(np.arange(1, 3), p=[0.4, 0.6])
            t_service = self._generate_service()
            yield env.timeout(t_service)
            t_end = np.around(env.now, 3)
            t_end = t + dt.timedelta(minutes=t_end*60)
            # print('%.3f customer %d departs' % (t_depart, customer))

            self.waiting_list.append((t_end - t_arrival).seconds)
            self.records.append({
                'customer': customer,
                'arrival_time': t_arrival.time().replace(microsecond=0),
                'service_minutes': np.around(t_service*60, 3),
                'start_time': t_start.time().replace(microsecond=0),
                'end_time': t_end.time().replace(microsecond=0),
                'waiting_time': (t_start - t_arrival).seconds,
                'system_time': (t_end - t_start).seconds,
                'busy_server': servers.count,
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
