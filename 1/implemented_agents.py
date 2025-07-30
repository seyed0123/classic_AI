from agent import AbstractSearchAgent
import heapq
import math

class BFSAgent(AbstractSearchAgent):
    def searching(self):
        que = [(self.s_start,self.s_start,0)]
        seened = []
        while len(que):
            point,parent,cost = que.pop(0)
            if point in self.VISITED:
                continue
            self.PARENT[point] = parent
            self.COST[point] = cost
            self.VISITED.add(point)
            seened.append(point)
            if point == self.s_goal:
                break
            for neighbor in self.get_neighbors(point):
                que.append((neighbor,point,cost+self.NEIGHBOR_COSTS[point][neighbor]))

        return self.extract_path(),seened


class BiIDDFSAgent(AbstractSearchAgent):
    def limit_dfs(self,node,visited,goal,parents,costs):
        point,parent,cost = node
        if cost > self.limit:
            return None
        visited.append(point)
        parents[point] = parent
        costs[point] = costs[parent] + 1
        if point == goal:
            return cost
        for neighbor in self.get_neighbors(point):
            if neighbor not in visited:
                ret = self.limit_dfs((neighbor,point,cost+1),visited,goal,parents,costs)
                if ret:
                    return ret
                


    def extract_path_re(self,start,parent,costs_2):
        path = []
        s = start
        l_cost = self.COST[start]
        while s != self.s_goal:
            path.append(s)
            s = parent[s]
            self.COST[s] = l_cost + 1
        path.append(self.s_goal)
        self.COST[self.s_goal] = l_cost + 1
        return path

    def extract_path(self,end,parent):
        path = []
        s = end
        while s != self.s_start:
            path.append(s)
            s = parent[s]
        path.append(self.s_start)
        path.reverse()
        return path


    def searching(self):
        self.limit = 1
        all_visited = []
        while True:
            visited = []
            parents = {}
            costs = {self.s_start:0}
            self.limit_dfs((self.s_start,self.s_start,0),visited,self.s_goal,parents,costs)
            

            visited_2 = []
            parents_2 = {}
            costs_2 = {self.s_goal:0}
            self.limit_dfs((self.s_goal,self.s_goal,0),visited_2,self.s_start,parents_2,costs_2)
            all_visited.extend(visited)
            all_visited.extend(visited_2)
            intersection = list(set(visited)&set(visited_2))
            if len(intersection)>0:
                break
            self.limit+=1
        
        self.COST = costs
        return self.extract_path(intersection[0],parents) + self.extract_path_re(intersection[0],parents_2,costs_2),all_visited
        
            
        
class AStarAgent(AbstractSearchAgent):
    def searching(self):
        que = [(0,0,self.s_start,self.s_start)]
        heapq.heapify(que)
        seened = []
        while len(que):
            f,g,point,parent = heapq.heappop(que)
            if point in self.VISITED:
                continue
            self.PARENT[point] = parent
            self.COST[point] = g
            self.VISITED.add(point)
            seened.append(point)
            if point == self.s_goal:
                break
            for neighbor in self.get_neighbors(point):
                if neighbor in self.teleports:
                    pass
                n_cost = round(self.NEIGHBOR_COSTS[point][neighbor],2)
                f = g + n_cost + self.get_h(neighbor,self.s_goal) 
                heapq.heappush(que,(f,g+n_cost,neighbor,point))

        return self.extract_path(),seened
    def get_h(self, s_from, s_to):
        dx = s_to[0] - s_from[0]
        dy = s_to[1] - s_from[1]
        distance = math.sqrt(dx ** 2 + dy ** 2)
        return distance


class UCSAgent(AbstractSearchAgent):
    def searching(self):
        que = [(0,self.s_start,self.s_start)]
        heapq.heapify(que)
        seened = []
        while len(que):
            cost,point,parent = heapq.heappop(que)
            if point in self.VISITED:
                continue
            self.PARENT[point] = parent
            self.COST[point] = cost
            self.VISITED.add(point)
            seened.append(point)
            if point == self.s_goal:
                break
            for neighbor in self.get_neighbors(point):
                if neighbor in self.teleports:
                    pass
                n_cost = round(self.NEIGHBOR_COSTS[point][neighbor],2)
                heapq.heappush(que,(cost+n_cost,neighbor,point))

        return self.extract_path(),seened
