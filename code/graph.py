import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from singlehouse import Singlehouse
from bungalow import Bungalow
from maison import Maison
from House import House
from shapely.geometry import box, Point


class Graph():
    def __init__(self, area):
        """
            Necessities for the visual representation
        """
        self.water = []
        self.width = 180
        self.depth = 160

        # Load the water data
        self.load_water(f"../Areas/{area}.csv")

        # Create area graph
        self.load_graph()


    def load_water(self, filename):
        """
            Loads the water that belongs to a specific neighborhood
        """
        # Read the file that contains the water data
        with open(filename, "r") as csv_file:
            next(csv_file)
            reader = csv.reader(csv_file)

            for counter, row in enumerate(reader):
                self.water.append([])
                for elem in row:
                    if elem[0].isnumeric():
                        coords = list(map(float,elem.split(','))) 
                        self.water[counter].append(coords)
                    else:
                        self.water[counter].append(elem)


    def load_graph(self):
        """
            Creates the map for the specific area
        """
        plt.xlabel("width")
        plt.ylabel("depth")
        plt.axis([0, self.width, 0, self.depth])
        
        # Display the neighborhood as green
        ax = plt.gca()
        ax.set_facecolor("green")
        
        for data in self.water:
            # Create a Rectangle patch in which water is displayed as blue
            rect = patches.Rectangle((data[1][0], data[1][1]),(data[2][0]-data[1][0]),(data[2][1]-data[1][1]),facecolor='b')
            # Add the patch to the Axes
            ax.add_patch(rect)

        # Save the graph
        plt.savefig('../plots/init_graph.png')
        

    def load_houses(self, houses):
        """
            Locate houses on the map
        """
        ax = plt.gca()

        for house in houses:
            rect = patches.Rectangle((house.corner_lowerleft[0], house.corner_lowerleft[1]),house.width, house.length,facecolor='r')
            # Add the patch to the Axes
            ax.add_patch(rect)

        # Save the graph
        plt.savefig('../plots/init_graph.png')


    def overlap(self, house, houses):
        """
            Checks for overlapping houses with each other, water or the edges of the graph.
            Returns True if a house overlaps.
        """
        # save the points of the structures in boxes to find intersection
        graph_box = box(0,0,self.width, self.depth)
        housebox1 = box(house.corner_lowerleft[0], house.corner_lowerleft[1], (house.return_upperright(house)[0]), (house.return_upperright(house)[1]))
        water_boxes = []
        for data in self.water:
            water_box = box(data[1][0], data[1][1], data[2][0], data[2][1])
            water_boxes.append(water_box)

        # check for overlap between edges graph and houses and save in list
        if housebox1.overlaps(graph_box):
            return True

        # check for intersection between water areas and houses and save in list
        for water_box in water_boxes:
            if housebox1.intersects(water_box):
                return True

        # check for intersections between different houses and save in list
        for house2 in houses:
            housebox2 = box(house2.corner_lowerleft[0], house2.corner_lowerleft[1], (house2.return_upperright(house2)[0]), (house2.return_upperright(house2)[1]))
            # IPV .CORNER_LOWERLEFT MET IDS OF STRUCTURE WERKEN OM ZEKER TE WETEN WELK HUIS
            if house.corner_lowerleft is not house2.corner_lowerleft and housebox1.intersects(housebox2):
                return True
                
        return False


    def closest_house(self, house, houses):
        """
            Checks which house is most nearby another house
            The output list returns a house and its freespace
        """
        output = []

        # save all the corners of the house
        house_pointlist = [house.corner_lowerleft, house.return_upperleft(house), house.return_upperright(house), house.return_lowerright(house)]

        for neigh_house in houses:
            # UITEINDELIJK MET ID OF STRUCTURE EN NIET LOWERLEFT
            if neigh_house.corner_lowerleft is not house.corner_lowerleft:
                # save all the corners of a neighbouring house
                neigh_pointlist = [neigh_house.corner_lowerleft, neigh_house.return_upperleft(neigh_house), neigh_house.return_upperright(neigh_house), neigh_house.return_lowerright(neigh_house)]
            
                # compare the points of given house and its neighbours to find shortest distance
                for housepoint in house_pointlist:
                    for neighpoint in neigh_pointlist:
                        distance = Point(housepoint[0],housepoint[1]).distance(Point(neighpoint[0],neighpoint[1]))
                        if output == []:
                            output.append(neigh_house)
                            output.append(distance) 
                        elif distance < output[1]:
                            output = []
                            output.append(neigh_house)
                            output.append(distance)

        return output


    def invalid(self, house, houses):
        """
            Checks if the freespace between houses is the same or larger than the minimum freespace required.
            Returns True if the freespace is invalid. 
        """
        nearest_neighbour = self.closest_house(house, houses)

        # Return houses with an invalid freespace distance
        if isinstance(house, Maison) and nearest_neighbour[1] < house.freespace:
            return True
        elif isinstance(house, Bungalow) and nearest_neighbour[1] < house.freespace:
            return True
        elif isinstance(house, Singlehouse) and  nearest_neighbour[1] < house.freespace:
            return True
    
        return False


    def randomly_assign_houses(self, houses):
        """
            Assigns coordinates to a single house. Checks if coordinate placement is valid.
            If not, new coordinates are assigned.
        """
        for house in houses:
            house.corner_lowerleft = house.random_lowerleft()
            while self.invalid(house, houses) or self.overlap(house, houses):
                house.corner_lowerleft = house.random_lowerleft()


    def houseprices(self, houses):
        """
            Calculates the final and total value of a house.
        """
        for house in houses:
            freespace = self.closest_house(house, houses)[1]
            extra_freespace = freespace - house.freespace
            price_increase = extra_freespace * house.percentage + 1
            house.price = round(house.price * price_increase)


    def all_houses_set(self):
        pass

    def move_house(self):
        pass

    def delete_house(self):
        pass

    def swap_house(self):
        pass


    def write_output(self, all_houses):
        """
            Writes the final output in a csv file.
        """
        with open('output.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow(["structure", "corner_1", "corner_2", "corner_3", "corner_4", "type"])
            total_price = []
            for house in all_houses:

                if isinstance(house, Singlehouse):
                    housetype = "SINGLEHOUSE"
                    writer.writerow([house.id, house.return_upperleft(house), house.corner_lowerleft, house.return_upperright(house), house.return_lowerright(house), housetype])
                elif isinstance(house, Bungalow):
                    housetype = "BUNGALOW"
                    writer.writerow([house.id, house.return_upperleft(house), house.corner_lowerleft, house.return_upperright(house), house.return_lowerright(house), housetype])
                elif isinstance(house, Maison):
                    housetype = "MAISON"
                    writer.writerow([house.id, house.return_upperleft(house), house.corner_lowerleft, house.return_upperright(house), house.return_lowerright(house), housetype])
                
                total_price.append(house.price)

            writer.writerow(["networth", sum(total_price)])