from owlready2 import *

# Load ontology
onto_path.append('data/ontology/')
ontology = get_ontology("data/ontology/maintenance.owl").load()
ontology.load()

with ontology:
	class Maintenance(Thing):
		response_classmap = {
			'maintenance.Damage': 'Maintenance related issue.',
			'maintenance.TenantInCharge': 'The tenant is responsible for resolving the issue.',
			'maintenance.LandlordInCharge': 'The landlord is responsible for resolving the issue.',
			'maintenance.BadUse': 'The damage is caused by the tenants bad use.',
			'maintenance.NaturalCause': 'The damage is not caused by the tenant.',
			'maintenance.SmallObject': 'The damaged object is small.',
			'maintenance.BigObject': 'The damaged object is big.',
			'maintenance.MajorAction': 'The damage requires a big effort to be resolved.',
			'maintenance.MinorAction': 'The damage requires a small effort to be resolved.',
		}
		ontology_properties = {
			'causedBy': 'What is the cause of the damage?',
			'hasSize': 'What object is damaged?',
			'require': 'What action is required to fix the damaged object?'
		}

		# Map resolved classes to their chatbot response
		def GetResolvedOutput(self, resolved_class):
			return self.response_classmap.get(str(resolved_class))

		# Get an explenation from a resolved class
		def GetResolvedExplenation(self, resolved_class):
			explenation = []
			for property in self.ontology_properties:
				if property in dir(resolved_class):
					reasons = getattr(resolved_class, property)
					if len(reasons) > 0:
						for reason in reasons:
							explenation.append(self.response_classmap.get(str(reason.__class__)))
			return explenation

		iter = 0
		def ResolveMaintenanceIssue(self, properties):
			self.iter += 1

			# Create an instance from the given properties
			onto_instance = ontology.Maintenance("maintenance_" + str(self.iter))
			for property in properties:
				setattr(onto_instance, property, properties.get(property))

			# Resolve the instance
			sync_reasoner()
			resolved_class = onto_instance.__class__
			resolved_classes = {
				'maintenance.TenantInCharge',
				'maintenance.LandlordInCharge'
			}
			if str(resolved_class) in resolved_classes:
				print('Conclusion: ' + self.GetResolvedOutput(onto_instance.__class__))
				support = self.GetResolvedExplenation(onto_instance)
				print('Why?: ' + str(support))
				return True, support
			else:
				print('Not yet resolved! Need more facts.')
				missing = []
				for property in self.ontology_properties:
					if property not in properties:
						missing.append({property: self.ontology_properties.get(property)})
				# TODO: Instead of returning all missing properties, find property that is most likely to solve the issue in the next iteration
				return False, missing

	# Define conclusions
	class TenantInCharge(Maintenance):
		equivalent_to = [
			ontology.Damage
			& (ontology.causedBy.some(ontology.BadUse) |
			   ontology.hasSize.some(ontology.SmallObject) |
			   ontology.require.some(ontology.MinorAction))
		]
	class LandlordInCharge(Maintenance):
		equivalent_to = [
			ontology.Damage
			& (ontology.causedBy.some(ontology.NaturalCause) &
			   ontology.hasSize.some(ontology.BigObject) &
			   ontology.require.some(ontology.MajorAction))
		]



maint = Maintenance()

# Iteration:
known_information = {
	# 'causedBy': [ontology.NaturalCause()],
	# 'hasSize': [ontology.SmallObject()],
	'require': [ontology.MinorAction()],
}

resolved = False
while not resolved:
	[resolved, support] = maint.ResolveMaintenanceIssue(known_information)
	print('done')

# Test
# test = ontology.search(type=ontology.MinorAction)
# test4 = ontology.search(uri="*")
# test_a = ontology.search(is_a=ontology.Maintenance)
# test_b = ontology.search(is_a=ontology.RequiredAction)
# test_c = ontology.search(is_a=ontology.MajorAction)
# test_d = ontology.search(is_a=ontology.Damage)
# test_e = ontology.search(is_a=ontology.TenantInCharge)

