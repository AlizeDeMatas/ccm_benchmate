from sqlalchemy.orm import declarative_base

# there are no tables in binders they will go to sequence and structure

from ccm_benchmate.variant.tables import *
from ccm_benchmate.literature.tables import *
from ccm_benchmate.structure.tables import *
from ccm_benchmate.sequence.tables import *
from ccm_benchmate.genome.tables import *
from ccm_benchmate.apis.tables import *
from ccm_benchmate.project.tables import *

Base = declarative_base()

