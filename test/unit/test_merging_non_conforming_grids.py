#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 13:37:55 2017

@author: eke001
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 11:19:02 2017

@author: eke001
"""
import unittest
import numpy as np
import scipy.sparse as sps

from porepy.grids.structured import TensorGrid
from porepy.fracs import non_conforming

class TestMeshMerging(unittest.TestCase):

    def test_merge_1d_grids_equal_nodes(self):
        g = TensorGrid(np.array([0, 1, 2]))
        g.compute_geometry()
        h, offset, g_in_comb, g_in_comb , _, _ =\
            non_conforming.merge_1d_grids(g, g, global_ind_offset=0, tol=1e-4)

        known_in_comb = np.array([0, 1, 2])

        assert np.allclose(g.nodes, h.nodes)
        assert offset == 3
        assert np.allclose(known_in_comb, g_in_comb)

    def test_merge_1d_grids_partly_equal_nodes(self):
        g = TensorGrid(np.array([0, 1, 2]))
        h = TensorGrid(np.array([0, 0.5, 1, 2]))
        g.compute_geometry()
        h.compute_geometry()
        gh, offset, g_in_comb, h_in_comb , _, _=\
            non_conforming.merge_1d_grids(g, h, global_ind_offset=0, tol=1e-4)

        known_nodes = np.array([0, 0.5, 1, 2])
        known_g_in_comb = np.array([0, 2, 3])
        known_h_in_comb = np.array([0, 1, 2, 3])
        assert np.allclose(known_nodes, gh.nodes[0])
        assert offset == 4
        assert np.allclose(known_g_in_comb, g_in_comb)
        assert np.allclose(known_h_in_comb, h_in_comb)

    def test_merge_1d_grids_unequal_nodes(self):
        # Unequal nodes along the x-axis
        g = TensorGrid(np.array([0, 1, 2]))
        h = TensorGrid(np.array([0, 0.5, 2]))
        g.compute_geometry()
        h.compute_geometry()
        gh, offset, g_in_comb, h_in_comb , _, _ =\
            non_conforming.merge_1d_grids(g, h, global_ind_offset=0, tol=1e-4)

        known_nodes = np.array([0, 0.5, 1, 2])
        known_g_in_comb = np.array([0, 2, 3])
        known_h_in_comb = np.array([0, 1, 3])
        assert np.allclose(known_nodes, gh.nodes[0])
        assert offset == 4
        assert np.allclose(known_g_in_comb, g_in_comb)
        assert np.allclose(known_h_in_comb, h_in_comb)

    def test_merge_1d_grids_rotation(self):
        #1d grids rotated
        g = TensorGrid(np.array([0, 1, 2]))
        g.nodes = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2]]).T
        g.compute_geometry()
        h = TensorGrid(np.array([0, 1, 2]))
        h.nodes = np.array([[0, 0, 0], [0.5, 0.5, 0.5], [2, 2, 2]]).T
        h.compute_geometry()

        gh, offset, g_in_comb, h_in_comb , _, _ =\
            non_conforming.merge_1d_grids(g, h, global_ind_offset=0)

        known_nodes = np.array([[0, 0, 0], [0.5, 0.5, 0.5], [1, 1, 1],
                                [2, 2, 2]]).T
        known_g_in_comb = np.array([0, 2, 3])
        known_h_in_comb = np.array([0, 1, 3])
        assert np.allclose(known_nodes, gh.nodes[0])
        assert offset == 4
        assert np.allclose(known_g_in_comb, g_in_comb)
        assert np.allclose(known_h_in_comb, h_in_comb)

    def test_update_face_nodes_equal_2d(self):
        data = np.ones(4)
        rows = np.array([0, 1, 2, 3])
        cols = np.array([0, 0, 1, 1])
        fn = sps.coo_matrix((data, (rows, cols)), shape=(4, 2))
        g = MockGrid(dim=2, num_faces=2, face_nodes=fn)

        delete_faces = np.array([0])
        new_face_ind = non_conforming.update_face_nodes(g, delete_faces, 1, 2)
        assert new_face_ind.size == 1
        assert new_face_ind[0] == 1
        fn_known = np.array([[0, 0], [0, 0], [1, 1], [1, 1]], dtype=np.bool)

        assert np.allclose(fn_known, g.face_nodes.A)

    def test_update_face_nodes_equal_3d(self):
        data = np.ones(6)
        rows = np.array([0, 1, 2, 3, 1, 2])
        cols = np.array([0, 0, 0, 1, 1, 1])
        fn = sps.coo_matrix((data, (rows, cols)), shape=(4, 2))
        g = MockGrid(dim=3, num_faces=2, face_nodes=fn)

        delete_faces = np.array([0])
        new_face_ind = non_conforming.update_face_nodes(g, delete_faces, 1, 0)
        assert new_face_ind.size == 1
        assert new_face_ind[0] == 1
        fn_known = np.array([[0, 1], [1, 1], [1, 1], [1, 0]], dtype=np.bool)

        assert np.allclose(fn_known, g.face_nodes.A)

    def test_update_face_nodes_add_none(self):
        # Only delete cells
        data = np.ones(4)
        rows = np.array([0, 1, 2, 3])
        cols = np.array([0, 0, 1, 1])
        fn = sps.coo_matrix((data, (rows, cols)), shape=(4, 2))
        g = MockGrid(dim=2, num_faces=2, face_nodes=fn)

        delete_faces = np.array([0])
        new_face_ind = non_conforming.update_face_nodes(g, delete_faces,
                                                        num_new_faces=0,
                                                        new_node_offset=2)
        assert new_face_ind.size == 0
        fn_known = np.array([[0], [0], [1], [1]], dtype=np.bool)

        assert np.allclose(fn_known, g.face_nodes.A)

    def test_update_face_nodes_remove_all(self):
        # only add cells
        data = np.ones(4)
        rows = np.array([0, 1, 2, 3])
        cols = np.array([0, 0, 1, 1])
        fn = sps.coo_matrix((data, (rows, cols)), shape=(4, 2))
        g = MockGrid(dim=2, num_faces=2, face_nodes=fn)

        delete_faces = np.array([0, 1])
        new_face_ind = non_conforming.update_face_nodes(g, delete_faces, 1, 2)
        assert new_face_ind.size == 1
        assert new_face_ind[0] == 0
        fn_known = np.array([[0], [0], [1], [1]], dtype=np.bool)

        assert np.allclose(fn_known, g.face_nodes.A)

    def test_update_cell_faces_no_update(self):
        # Same number of delete and new faces
        #cell-face
        data = np.ones(3)
        rows = np.array([0, 1, 2])
        cols = np.array([0, 0, 0])
        cf = sps.coo_matrix((data, (rows, cols)), shape=(3, 1))
        # face-nodes
        fn_orig = np.array([[0, 1, 2, 3], [1, 2, 3, 4]])

        data = np.ones(6)
        rows = np.array([1, 2, 2, 3, 0, 1])
        cols = np.array([0, 0, 1, 1, 2, 2])
        fn = sps.coo_matrix((data, (rows, cols)), shape=(4, 3))

        nodes = np.array([[0, 1, 2, 3], [0, 0, 0, 0], [0, 0, 0, 0]])
        nodes_orig = nodes
        g = MockGrid(dim=2, num_faces=3, face_nodes=fn, num_cells=1, cell_faces=cf,
                     nodes=nodes)
        delete_faces = np.array([0])
        new_faces = np.array([2])
        in_combined = np.array([0, 1])
        non_conforming.update_cell_faces(g, delete_faces, new_faces, in_combined,
                                         fn_orig, nodes_orig)

        cf_expected = np.array([0, 1, 2])
        assert np.allclose(np.sort(g.cell_faces.indices), cf_expected)

    def test_update_cell_faces_one_by_two(self):
        #cell-face
        data = np.ones(3)
        rows = np.array([0, 1, 2])
        cols = np.array([0, 0, 0])
        cf = sps.coo_matrix((data, (rows, cols)), shape=(3, 1))
        # face-nodes
        fn_orig = np.array([[0, 1, 2, 3], [1, 2, 3, 4]])

        data = np.ones(8)
        rows = np.array([2, 3, 3, 4, 0, 1, 1, 2])
        cols = np.array([0, 0, 1, 1, 2, 2, 3, 3])
        fn = sps.coo_matrix((data, (rows, cols)), shape=(5, 4))

        nodes = np.array([[0, 0.5, 1, 2, 3], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
        nodes_orig = nodes[:, [0, 2, 3, 4]]
        g = MockGrid(dim=2, num_faces=4, face_nodes=fn, num_cells=1, cell_faces=cf,
                     nodes=nodes)
        delete_faces = np.array([0])
        new_faces = np.array([2, 3])
        in_combined = np.array([0, 2])
        non_conforming.update_cell_faces(g, delete_faces, new_faces, in_combined,
                                         fn_orig, nodes_orig)

        cf_expected = np.array([0, 1, 2, 3])
        assert np.allclose(np.sort(g.cell_faces.indices), cf_expected)


    def test_update_cell_faces_one_by_two_reverse_order(self):
        #cell-face
        data = np.ones(3)
        rows = np.array([0, 1, 2])
        cols = np.array([0, 0, 0])
        cf = sps.coo_matrix((data, (rows, cols)), shape=(3, 1))
        # face-nodes
        fn_orig = np.array([[0, 1, 2, 3], [1, 2, 3, 4]])

        data = np.ones(8)
        rows = np.array([2, 3, 3, 4, 0, 1, 1, 2])
        cols = np.array([0, 0, 1, 1, 2, 2, 3, 3])
        fn = sps.coo_matrix((data, (rows, cols)), shape=(5, 4))

        nodes = np.array([[0, 0.5, 1, 2, 3], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
        nodes_orig = nodes[:, [0, 2, 3, 4]]
        g = MockGrid(dim=2, num_faces=4, face_nodes=fn, num_cells=1, cell_faces=cf,
                     nodes=nodes)
        delete_faces = np.array([0])
        new_faces = np.array([3, 2])
        in_combined = np.array([0, 2])
        non_conforming.update_cell_faces(g, delete_faces, new_faces, in_combined,
                                         fn_orig, nodes_orig)

        cf_expected = np.array([0, 1, 2, 3])
        assert np.allclose(np.sort(g.cell_faces.indices), cf_expected)

    def test_update_cell_faces_delete_shared(self):
        # Two cells sharing a face
        #cell-face
        data = np.ones(5)
        rows = np.array([0, 1, 2, 2, 3])
        cols = np.array([0, 0, 0, 1, 1])
        cf = sps.coo_matrix((data, (rows, cols)), shape=(4, 2))
        # face-nodes
        fn_orig = np.array([[0, 1, 2, 3], [1, 2, 3, 4]])

        data = np.ones(10)
        rows = np.array([0, 1, 1, 2, 4, 5, 2, 3, 3, 4])
        cols = np.array([0, 0, 1, 1, 2, 2, 3, 3, 4, 4])
        fn = sps.coo_matrix((data, (rows, cols)), shape=(6, 5))

        nodes = np.array([[0, 1, 2, 2.5, 3, 4],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]])
        nodes_orig = nodes[:, [0, 1, 2, 4, 5]]
        g = MockGrid(dim=2, num_faces=5, face_nodes=fn, num_cells=2, cell_faces=cf,
                     nodes=nodes)
        delete_faces = np.array([2])
        new_faces = np.array([3, 4])
        in_combined = np.array([0, 2])
        non_conforming.update_cell_faces(g, delete_faces, new_faces, in_combined,
                                         fn_orig, nodes_orig)

        cf_expected = np.array([[1, 1, 0, 1, 1],
                                [0, 0, 1, 1, 1]], dtype=np.bool).T
        assert np.allclose(np.abs(g.cell_faces.toarray()), cf_expected)

    def test_update_cell_faces_delete_shared_reversed(self):
        #cell-face
        data = np.ones(5)
        rows = np.array([0, 1, 2, 2, 3])
        cols = np.array([0, 0, 0, 1, 1])
        cf = sps.coo_matrix((data, (rows, cols)), shape=(4, 2))
        # face-nodes
        fn_orig = np.array([[0, 1, 2, 3], [1, 2, 3, 4]])

        data = np.ones(10)
        rows = np.array([0, 1, 1, 2, 4, 5, 2, 3, 3, 4])
        cols = np.array([0, 0, 1, 1, 2, 2, 3, 3, 4, 4])
        fn = sps.coo_matrix((data, (rows, cols)), shape=(6, 5))

        nodes = np.array([[0, 1, 2, 2.5, 3, 4],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]])
        nodes_orig = nodes[:, [0, 1, 2, 4, 5]]
        g = MockGrid(dim=2, num_faces=5, face_nodes=fn, num_cells=2, cell_faces=cf,
                     nodes=nodes)
        delete_faces = np.array([2])
        new_faces = np.array([4, 3])
        in_combined = np.array([0, 2])
        non_conforming.update_cell_faces(g, delete_faces, new_faces, in_combined,
                                         fn_orig, nodes_orig)

        cf_expected = np.array([[1, 1, 0, 1, 1],
                                [0, 0, 1, 1, 1]], dtype=np.bool).T
        assert np.allclose(np.abs(g.cell_faces.toarray()), cf_expected)

    def test_update_cell_faces_change_all(self):
        data = np.ones(2)
        rows = np.array([0, 1])
        cols = np.array([0, 1])
        cf = sps.coo_matrix((data, (rows, cols)), shape=(2, 2))
        # face-nodes
        fn_orig = np.array([[0, 1], [1, 2]])

        data = np.ones(10)
        rows = np.array([0, 1, 1, 2, 2, 3, 3, 4, 4, 5])
        cols = np.array([0, 0, 1, 1, 2, 2, 3, 3, 4, 4])
        fn = sps.coo_matrix((data, (rows, cols)), shape=(6, 5))

        nodes = np.array([[0, 1, 2, 3, 4, 5],
                          [0, 0, 0, 0, 0, 0],
                          [0, 0, 0, 0, 0, 0]])
        nodes_orig = nodes[:, [0, 2, 5]]
        g = MockGrid(dim=2, num_faces=5, face_nodes=fn, num_cells=2, cell_faces=cf,
                     nodes=nodes)
        delete_faces = np.array([0, 1])
        new_faces = np.array([0, 1, 2, 3, 4, 5])
        in_combined = np.array([0, 2, 5])
        non_conforming.update_cell_faces(g, delete_faces, new_faces, in_combined,
                                         fn_orig, nodes_orig)

        cf_expected = np.array([[1, 1, 0, 0, 0],
                                [0, 0, 1, 1, 1]], dtype=np.bool).T
        assert np.allclose(np.abs(g.cell_faces.toarray()), cf_expected)

    if __name__ == '__main__':
        unittest.main()

class MockGrid():
    """ Class with attributes similar to (some of) those in a real grid. Used
    for testing purposes
    """

    def __init__(self, dim, num_faces=None, face_nodes=None, nodes=None,
                 cell_faces=None, num_cells=None):

        self.dim = dim
        self.face_nodes = face_nodes.tocsc()
        self.num_faces = num_faces
        if cell_faces is not None:
            self.cell_faces = cell_faces.tocsc()
        self.num_cells = num_cells


        self.num_nodes = self.face_nodes.shape[0]
        self.nodes = np.zeros((3, self.num_nodes))
