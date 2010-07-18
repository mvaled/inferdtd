#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#    Copyright (C) 2007  Manuel Vázquez Acosta <mva.led@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import unittest
from inferdtd.Graph import Graph
#import inferdtd.Graph

class NodesTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(nodes = range(1, 10))

    def testLenWhenInitNodeArgument(self):
        self.assertEqual(len(self.graph), len(range(1, 10)))

    def testLenWhenAddedNode(self):
        previouslen = len(self.graph)
        self.graph.addnode(1000)
        self.assertEqual(len(self.graph), previouslen + 1)

    def testLenWhenNonAddedNode(self):
        previouslen = len(self.graph)
        self.graph.addnode(1)
        self.assertEqual(len(self.graph), previouslen)

    def testLenWhenRemovedNode(self):
        previouslen = len(self.graph)
        self.graph.removenode(1)
        self.assertEqual(len(self.graph), previouslen - 1)

    def testLenWhenNonRemovedNode(self):
        previouslen = len(self.graph)
        self.graph.removenode(1000)
        self.assertEqual(len(self.graph), previouslen)

    def testAddedNode(self):
        self.graph.addnode(1)
        self.assert_(1 in self.graph.nodes)

    def testRemovedNode(self):
        self.graph.removenode(5)
        self.assert_(5 not in self.graph.nodes)

class EdgesTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(nodes = range(1, 10), edges = [(1,2)])

    def testLenWhenInitEdges(self):
        self.assertEqual(len(self.graph.edges), 1)

    def testInitNonEdges(self):
        self.assertRaises(AssertionError, Graph,
                          nodes = range(1, 10), edges = [(1,22)])

    def testLenWhenAddedEdge(self):
        previouslen = len(self.graph.edges)
        self.graph.addedge((2, 3))
        self.assertEqual(len(self.graph.edges), previouslen + 1)

    def testLenWhenNonAddedEdge(self):
        previouslen = len(self.graph.edges)
        self.graph.addedge((1, 2))
        self.assertEqual(len(self.graph.edges), previouslen)

    def testAddedEdge(self):
        self.graph.addedge((2, 3))
        self.assert_((2, 3) in self.graph.edges)

    def testErrorWhenAddingEdgeWithInvalidNode(self):
        self.assertRaises(AssertionError, self.graph.addedge, (1, 45))

    def testRemovedEdge(self):
        self.graph.removeedge((1, 2))
        self.assert_((1, 2) not in self.graph.edges)

    def testRemoveInvalidEdge(self):
        self.graph.removeedge((2, 3))
        self.assert_((2, 3) not in self.graph.edges)

    def testRemoveEdgeWithInvalidNode(self):
        self.graph.removeedge((2, 33))
        self.assert_((2, 33) not in self.graph.edges)

class EdgePropertiesTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(nodes = range(1, 10))
        self.graph.addedge((1, 2))
        self.graph.addedge((2, 3))
        self.graph.addedge((3, 1))
        self.graph.addedge((4, 5))

    def testIsolatedNode(self):
        nodes = self.graph.getedgesintonode(6)
        self.assertEqual(nodes, [])
        nodes = self.graph.getedgesoutofnode(6)
        self.assertEqual(nodes, [])

    def testNonIsolatedNode(self):
        nodes = self.graph.getedgesintonode(2)
        self.assertEqual(nodes, [(1, 2)])
        nodes = self.graph.getedgesoutofnode(2)
        self.assertEqual(nodes, [(2, 3)])

    def testAddEdge(self):
        self.graph.addedge((3, 5))
        self.assert_((3, 5) in self.graph.getedgesintonode(5))
        self.assert_((3, 5) in self.graph.getedgesoutofnode(3))
        self.assert_((3, 5) in self.graph.edges)

    def testRemoveEdge(self):
        self.graph.removeedge((1, 2))
        self.assert_((1, 2) not in self.graph.getedgesintonode(2))
        self.assert_((1, 2) not in self.graph.getedgesoutofnode(1))
        self.assert_((1, 2) not in self.graph.edges)

class ReplacementTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(nodes = range(1, 6))
        self.graph.addedge((1, 2))
        self.graph.addedge((2, 3))
        self.graph.addedge((3, 1))
        self.graph.addedge((4, 5))

    def testLenWhenNodeReplacement(self):
        l = len(self.graph)
        self.graph.replacenode(2, 21)
        self.assertEqual(len(self.graph), l)

    def testNodeReplacement(self):
        self.graph.addedge((2, 2))
        self.graph.replacenode(2, 21)
        self.assert_(2 not in self.graph.nodes)
        self.assert_(21 in self.graph.nodes)
        self.assert_((1, 21) in self.graph.edges)
        self.assert_((21, 3) in self.graph.edges)

    def testEdgeReplacement(self):
        self.graph.replaceedge((1, 2), (4, 3))
        self.assert_((1, 2) not in self.graph.edges)
        self.assert_((4, 3) in self.graph.edges)


class EmptyObject(object):
    def __init__(self, value):
        self.value = value

    def matchesemptystring(self):
        return True

    def __repr__(self):
        return "<%s>" % repr(self.value)

class PredSuccTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(nodes = range(1, 8))
        self.graph.addedge((1, 3))
        self.graph.addedge((2, 3))
        self.graph.addedge((3, 4))
        self.graph.addedge((4, 5))
        self.graph.addedge((5, 6))
        self.graph.addedge((7, 5))
        self.eo4 = eo4 = EmptyObject(4)
        self.eo3 = eo3 = EmptyObject(3)
        self.eo5 = eo5 = EmptyObject(5)
        self.graph.replacenode(4, eo4)
        self.graph.replacenode(3, eo3)
        self.graph.replacenode(5, eo5)

    def testInitialPredSet(self):
        self.assertEqual(self.graph.pred(4), set([]))
        self.assertEqual(self.graph.pred(self.eo4), set([1, 2, self.eo3]))

    def testInitialSuccSet(self):
        self.assertEqual(self.graph.succ(4), set([]))
        self.assertEqual(self.graph.succ(self.eo3), set([self.eo4, self.eo5, 6]))

    def testPredSet(self):
        self.graph.replacenode(self.eo3, 3)
        self.assertEqual(self.graph.pred(self.eo4), set([3]))
        self.graph.replacenode(3, self.eo3)
        self.assertEqual(self.graph.pred(self.eo4), set([1, 2, self.eo3]))

    def testSuccSet(self):
        self.graph.replacenode(self.eo4, 4)
        self.assertEqual(self.graph.succ(self.eo3), set([4]))
        self.graph.replacenode(4, self.eo4)
        self.assertEqual(self.graph.succ(self.eo3), set([self.eo4, self.eo5, 6]))


if __name__ == '__main__':
    unittest.main()
