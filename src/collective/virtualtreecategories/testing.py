from Products.PloneTestCase import ptc

from collective.testcaselayer import ptc as tcl_ptc

ptc.setupPloneSite()

class Layer(tcl_ptc.BasePTCLayer):
    """Install collective.virtualtreecategories"""

    def afterSetUp(self):
        self.addProfile('collective.virtualtreecategories:default')


from zope.annotation.attribute import AttributeAnnotations
from zope.component import provideAdapter
from collective.testcaselayer import ztc as tcl_ztc

class AttributeAnnotationsLayer(tcl_ztc.BaseZTCLayer):
    """Install annotations """

    def afterSetUp(self):
        provideAdapter(AttributeAnnotations)

layer = Layer([tcl_ptc.ptc_layer])
annotations_layer = AttributeAnnotationsLayer([tcl_ztc.ztc_layer])
