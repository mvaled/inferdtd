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
from inferdtd.AutomataInferrer import infer_automata
from inferdtd.AutomataInferrer import StartNode
from inferdtd.AutomataInferrer import EndNode

class InferenceTest(unittest.TestCase):
    def setUp(self):
        self.graph = infer_automata(["bacacdacde", "cbacdbacde"])

    def testNodesCompliance(self):
        for x in "bacacdacde"+"cbacdbacde":
            self.assert_(x in self.graph.nodes)

    def testInferredEdges(self):
        self.assert_(("b", "a") in self.graph.edges)
        self.assert_(("a", "c") in self.graph.edges)
        self.assert_(("c", "a") in self.graph.edges)
        self.assert_(("c", "d") in self.graph.edges)
        self.assert_(("d", "a") in self.graph.edges)
        self.assert_(("d", "e") in self.graph.edges)
        self.assert_(("c", "b") in self.graph.edges)
        self.assert_(("d", "b") in self.graph.edges)
        self.assert_((StartNode, "b") in self.graph.edges)
        self.assert_((StartNode, "c") in self.graph.edges)
        self.assert_(("e", EndNode) in self.graph.edges)
        self.assertEqual(len(self.graph.edges), 11) # Those 11 edges

if __name__ == '__main__':
    unittest.main()
