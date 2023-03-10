import torch

from mlcvs.core.transform import Transform
from mlcvs.core.transform.utils import compute_distances_matrix,apply_cutoff

from typing import Union

__all__ = ["AdjacencyMatrix"]

class AdjacencyMatrix(Transform):
    """
    Adjacency matrix transform, compute the adjacency matrix for a set of atoms from their positions
    """

    def __init__(self,
                 mode : str,
                 cutoff : float, 
                 n_atoms : int,
                 PBC: bool,
                 real_cell: Union[float, list],
                 scaled_coords : bool,
                 switching_function = None) -> torch.Tensor:
        """Initialize an adjacency matrix object.

        Parameters
        ----------
        mode : str
            Mode for cutoff application, either:
            - 'continuous': applies a switching function to the distances wich can be specified with switching_fucniton keyword, has stable derivatives
            - 'discontinuous': set at zero everything above the cutoff and one below, derivatives may be be incorrect
        cutoff : float
            Cutoff for the adjacency criterion 
        n_atoms : int
            Number of atoms in the system
        PBC : bool
            Switch for Periodic Boundary Conditions use
        real_cell : Union[float, list]
            Dimensions of the real cell, orthorombic-like cells only
        scaled_coords : bool
            Switch for coordinates scaled on cell's vectors use
        switching_function : _type_, optional
            Switching function to be applied for the cutoff, can be either initialized as a utils/SwitchingFunctions class or a simple function, by default None

        Returns
        -------
        torch.Tensor
            Adjacency matrix of all the n_atoms according to cutoff
        """
        super().__init__()

        # parse args
        self.mode = mode
        self.cutoff = cutoff 
        self.n_atoms = n_atoms
        self.PBC = PBC
        self.real_cell = real_cell
        self.scaled_coords = scaled_coords
        self.switching_function = switching_function

    def compute_adjacency_matrix(self, pos, mode):
        dist = compute_distances_matrix(pos=pos,
                                        n_atoms=self.n_atoms,
                                        PBC=self.PBC,
                                        real_cell=self.real_cell,
                                        scaled_coords=self.scaled_coords)
        adj_matrix = apply_cutoff(dist, self.cutoff, mode=mode, switching_function = self.switching_function)
        return adj_matrix

    def forward(self, x: torch.Tensor):
        x = self.compute_adjacency_matrix(x, mode=self.mode)
        return x

def test_adjacency_matrix():
    from mlcvs.core.transform.utils import SwitchingFunctions

    pos = torch.Tensor([ [ [0., 0., 0.],
                           [1., 1., 1.] ],
                         [ [0., 0., 0.],
                           [1., 1.1, 1.] ] ]
                      )
    
    real_cell = torch.Tensor([1., 2., 1.])
    cutoff = 1.8
    switching_function=SwitchingFunctions('Fermi', cutoff, options={'q':0.01})
    
    def silly_switch(x):
        return torch.pow(x, 2)
    switching_function = silly_switch
    model = AdjacencyMatrix(mode = 'continuous',
                            cutoff = cutoff, 
                            n_atoms = 2,
                            PBC = True,
                            real_cell = real_cell,
                            scaled_coords = False,
                            switching_function=switching_function)
    out = model(pos)
    print(out)

if __name__ == "__main__":
    test_adjacency_matrix()