#ifndef PAIRINGMODULE_H
#define PAIRINGMODULE_H

#include <Python.h>
#include <structmember.h>
#include <longintrepr.h>
#include <stdlib.h>
#include <gmp.h>
#include <pbc/pbc.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "sha1.h"
#include "benchmarkmodule.h"
#include "base64.h"

//#define DEBUG	1
//#define TRUE	1
//#define FALSE	0
#define MAX_LEN 2048
#define HASH_LEN 20
#define MAX_BENCH_OBJECTS	2
// define element_types
enum Group {ZR, G1, G2, GT, NONE_G};
typedef enum Group GroupType;

/* Index numbers for different hash functions.  These are all implemented as SHA1(index || message).	*/
#define HASH_FUNCTION_ELEMENTS			0
#define HASH_FUNCTION_STR_TO_Zr_CRH		1
#define HASH_FUNCTION_Zr_TO_G1_ROM		2
#define HASH_FUNCTION_STRINGS			3

#ifdef DEBUG
#define debug_e(...)	element_printf("DEBUG: "__VA_ARGS__)
#else
#define debug_e(...)
#endif

PyTypeObject ElementType;
PyTypeObject PairingType;
static PyObject *ElementError;
static Benchmark *dBench;
#define PyElement_Check(obj) PyObject_TypeCheck(obj, &ElementType)
#define PyPairing_Check(obj) PyObject_TypeCheck(obj, &PairingType)
#if PY_MAJOR_VERSION >= 3
/* check for both unicode and bytes objects */
#define PyBytes_CharmCheck(obj) PyUnicode_Check(obj) || PyBytes_Check(obj)
#else
/* check for just unicode stuff */
#define PyBytes_CharmCheck(obj)	PyUnicode_Check(obj) || PyString_Check(obj)
#endif

#if PY_MAJOR_VERSION >= 3
/* if unicode then add extra conversion step. two possibilities: unicode or bytes */
#define PyBytes_ToString(a, obj) \
	if(PyUnicode_Check(obj)) { obj = PyUnicode_AsUTF8String(obj); } \
	a = PyBytes_AS_STRING(obj);
#else
/* treat everything as string in 2.x */
#define PyBytes_ToString(a, obj) a = PyString_AsString(obj);
#endif

// static Benchmark *dObjects[MAX_BENCH_OBJECTS], *activeObject = NULL;

PyMethodDef Element_methods[];
PyMethodDef pairing_methods[];
PyMemberDef Element_members[];
PyNumberMethods element_number;

typedef struct {
	PyObject_HEAD
	pbc_param_t p;
	pairing_t pair_obj;
	int safe;
} Pairing;

typedef struct {
    PyObject_HEAD
	char *params;
	char *param_buf;
//	pairing_ptr pairing;
	Pairing *pairing;
	element_t e;
	GroupType element_type;
    int elem_initialized;
	int safe_pairing_clear;
} Element;


#define IS_PAIRING_OBJ_NULL(obj) \
	if(obj->pairing == NULL) {	\
		PyErr_SetString(ElementError, "pairing structure not initialized.");	\
		return NULL;	\
	}


#define Check_Elements(o1, o2)  PyElement_Check(o1) && PyElement_Check(o2)

#define Check_Types2(o1, o2, lhs_o1, rhs_o2, longLHS_o1, longRHS_o2)  \
	if(PyElement_Check(o1)) { \
		lhs_o1 = (Element *) o1; \
		debug("found a lhs element.\n"); \
    } \
	else if(PyLong_Check(o1)) { \
		longLHS_o1 = TRUE;  } \
							  \
	if(PyElement_Check(o2)) {  \
		rhs_o2 = (Element *) o2; \
		debug("found a rhs element.\n"); \
    } \
	else if(PyLong_Check(o2)) {  \
		longRHS_o2 = TRUE; }	\

#define set_element_ZR(obj, value)  \
    if(value == 0)		\
       element_set0(obj);   \
	else if(value == 1)		\
	   element_set1(obj);	\
    else {  element_set_si(obj, (signed int) value); }

#define VERIFY_GROUP(g) \
	if(PyElement_Check(g) && g->safe_pairing_clear == FALSE) {	\
		PyErr_SetString(ElementError, "invalid group object specified.");  \
		return NULL;  } 	\
	if(g->pairing == NULL) {	\
		PyErr_SetString(ElementError, "pairing object is NULL.");	\
		return NULL;  }		\



PyObject *Element_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int Element_init(Element *self, PyObject *args, PyObject *kwds);
PyObject *Element_print(Element* self);
PyObject *Element_call(Element *elem, PyObject *args, PyObject *kwds);
void	Element_dealloc(Element* self);
Element *convertToZR(PyObject *LongObj, PyObject *elemObj);

PyObject *Apply_pairing(Element *self, PyObject *args);
PyObject *sha1_hash(Element *self, PyObject *args);

int exp_rule(GroupType lhs, GroupType rhs);
int mul_rule(GroupType lhs, GroupType rhs);
int add_rule(GroupType lhs, GroupType rhs);
int sub_rule(GroupType lhs, GroupType rhs);
int div_rule(GroupType lhs, GroupType rhs);
int pair_rule(GroupType lhs, GroupType rhs);
void print_mpz(mpz_t x, int base);
#endif
