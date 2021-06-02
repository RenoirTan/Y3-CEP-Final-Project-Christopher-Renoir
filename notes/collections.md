Collections:

	*students:
		students._id : ObjectId
		students.username : string
		students.encryptedUserPass : string
		students.name : string
		students.alias : string
		students.parents : array
			parents[i] : ObjectId
		students.dateUpdated : ISODatetime
	

	*staff:
		staff._id : ObjectId
		staff.username : string
		staff.encryptedUserPass : string
		staff.prefix : string
		staff.name : string
		staff.alias : string
		staff.dateUpdated : ISODatetime
			
	
	*parents:
		parents._id : ObjectId
		parents.username : string
		parents.encryptedUserPass : string
		parents.prefix : string
		parents.name : string
		parents.alias : string
		parents.type : string
		parents.dateUpdated : ISODatetime

	
	*groups:
		groups._id : ObjectId
		groups.name : string
		groups.tags : array
			tags[i] : string
		groups.dateUpdated : ISODatetime
	

	*studentsGroups:
		studentsGroups._id : ObjectId
		studentsGroups.student : ObjectId
		studentsGroups.group : ObjectId
	

	*staffGroups:
		staffGroups._id : ObjectId
		staffGroups.staff : ObjectId
		staffGroups.group : ObjectId
	

	*forms:
		forms._id : ObjectId
		forms.type : string
		forms.title : string
		forms.body : string
		forms.author : ObjectId (staff._id)
		forms.datePosted : ISODatetime
		forms.bluetick : array of objects
			forms.bluetick[i].reader : ObjectId
			forms.bluetick[i].dateRead : ISODatetime
	#	For later
	#	forms.audience : array
	#		groups[i] : ObjectId
	#	forms.questions : array of arrays
	#		forms.questions[i].question : int
	#		forms.questions[i].body : string
	#		forms.questions[i].type : string (mcq/oeq)
	#		forms.questions[i].options : array of char, string or int


	✓ "students",
	✓ "staff",
	✓ "parents",
	✓ "groups", # Classes, Groups(Eg. Subjects) and Student-Parent
	✓ "studentsGroup",
	✓ "staffGroup",
	✓(kinda) "forms", # Announcements, forms, quizzes/polls
	"formsResponses", # Responses to `forms`
	"grades", # Grades to groups:students
	"appointments" # Appointments (timer notifications, low priority)