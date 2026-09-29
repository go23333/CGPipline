#include <python2.7\Python.h>

#include "maya/MSelectionList.h"
#include "maya/MDagPath.h"
#include "maya/MString.h"
#include "maya/MDoubleArray.h"
#include "maya/MIntArray.h"
#include "maya/MFnMesh.h"
#include "maya/MFnSkinCluster.h"
#include "maya/MFnSingleIndexedComponent.h"
#include "maya/MPointArray.h"
#include "maya/MGlobal.h"
#include "maya/MPlug.h"
#include "maya/MFnDoubleArrayData.h"
#include "maya/MVector.h"
#include "maya/MVectorArray.h"
#include "maya/MPoint.h"
#include "maya/MItMeshVertex.h"

#include <tbb/tbb.h>

#include <set>
#include <vector>
#include <map>
#include <string>

using namespace std;

#define PyMArry(AttyT, ElemeT) void py_to_c(PyObject* py_obj, AttyT& c_obj) {py_list_to_m_arr<AttyT, ElemeT>(py_obj, c_obj);}
#define TV(t, v) t v;py_to_c(PyTuple_GetItem(args, i), v);i++
#define PyToC(fun, tvs, vs) static PyObject* fun(PyObject* self, PyObject* args){int i=0;tvs fun vs;return Py_None;}
#define PyToC2(fun,t0, t1) PyToC(fun, TV(t0, v0);TV(t1, v1);,(v0, v1))
#define PyToC3(fun,t0, t1, t2) PyToC(fun, TV(t0, v0);TV(t1, v1);TV(t2, v2);,(v0, v1, v2))
#define PyToC4(fun,t0, t1, t2, t3) PyToC(fun, TV(t0, v0);TV(t1, v1);TV(t2, v2);TV(t3, v3);,(v0, v1, v2, v3))
#define PyToC5(fun,t0, t1, t2, t3, t4) PyToC(fun, TV(t0, v0);TV(t1, v1);TV(t2, v2);TV(t3, v3);TV(t4, v4);,(v0, v1, v2, v3, v4))
#define PyToC6(fun,t0, t1, t2, t3, t4, t5) PyToC(fun, TV(t0, v0);TV(t1, v1);TV(t2, v2);TV(t3, v3);TV(t4, v4);TV(t5, v5);,(v0, v1, v2, v3, v4, v5))

void py_to_c(PyObject* py_obj, MString& c_obj) {
    c_obj = PyString_AsString(py_obj);
}

void py_to_c(PyObject* py_obj, int& c_obj) {
    c_obj = PyInt_AsLong(py_obj);
}

void py_to_c(PyObject* py_obj, double& c_obj) {
    c_obj = PyFloat_AsDouble(py_obj);
}

void py_to_c(PyObject* py_obj, MPoint& c_obj) {
    py_to_c(PyList_GetItem(py_obj, 0), c_obj.x);
    py_to_c(PyList_GetItem(py_obj, 1), c_obj.y);
    py_to_c(PyList_GetItem(py_obj, 2), c_obj.z);
}

void py_to_c(PyObject* py_obj, MVector& c_obj) {
    py_to_c(PyList_GetItem(py_obj, 0), c_obj.x);
    py_to_c(PyList_GetItem(py_obj, 1), c_obj.y);
    py_to_c(PyList_GetItem(py_obj, 2), c_obj.z);
}

template <class ArryT, class ElemeT>
void py_list_to_m_arr(PyObject* py_obj, ArryT& c_obj) {
    int length = (int)PyObject_Length(py_obj);
    c_obj.setLength(length);
    for (int i = 0; i < length; i++) {
        ElemeT c_elem;
        PyObject* py_elem = PyList_GetItem(py_obj, i);
        py_to_c(py_elem, c_elem);
        c_obj[i] = c_elem;
    }
}
PyMArry(MIntArray, int)
PyMArry(MDoubleArray, double)
PyMArry(MVectorArray, MVector)
PyMArry(MPointArray, MPoint)

void py_to_c(PyObject* py_obj, vector<string>& c_obj) {
    int length = (int)PyObject_Length(py_obj);
    c_obj.clear();
    for (int i = 0; i < length; i++) {
        c_obj.push_back(PyString_AsString(PyList_GetItem(py_obj, i)));
    }
}

void find_by_name(MString name, MDagPath& dag_path) {
    MSelectionList selection_list;
    selection_list.add(name);
    selection_list.getDagPath(0, dag_path);
}

void find_by_name(MString name, MDagPath& dag_path, MObject & components) {
    MSelectionList selection_list;
    selection_list.add(name);
    selection_list.getDagPath(0, dag_path, components);
}

void find_by_name(MString name, MObject& depend_node) {
    MSelectionList selection_list;
    selection_list.add(name);
    selection_list.getDependNode(0, depend_node);
}


void set_paint_weights(MString skin_cluster_name, MDoubleArray& paint_weights) {
    MObject depend_node;
    find_by_name(skin_cluster_name, depend_node);
    MFnDependencyNode fn_depend_node(depend_node);
    MPlug ptw_plug = fn_depend_node.findPlug("ptw", false);
    MFnDoubleArrayData double_array_data;
    MObject double_array_object = double_array_data.create(paint_weights);
    ptw_plug.setMObject(double_array_object);
    MObject temp_obj = ptw_plug.asMObject();
    MFnDoubleArrayData temp_double_array_data(temp_obj);
    MDoubleArray temp_array = temp_double_array_data.array();
}

void get_mesh_points(MString polygon_name, MPointArray& points) {
    MDagPath dag_path;
    find_by_name(polygon_name, dag_path);
    MFnMesh fn_mesh(dag_path);
    fn_mesh.getPoints(points);
}

void get_weights(MString polygon_name, MString skin_cluster_name, MIntArray& indices, MDoubleArray& weights) {
    MDagPath path;
    MObject components;
    MObject skin_depend_node;
    find_by_name(polygon_name + ".vtx[*]", path, components);
    find_by_name(skin_cluster_name, skin_depend_node);
    MFnSingleIndexedComponent fn_component;
    MFnSkinCluster fn_skin(skin_depend_node);
    fn_skin.getWeights(path, components, indices, weights);
}


void get_weights(MString polygon_name, MString skin_cluster_name, MIntArray& indices, MIntArray& vtx_ids, MDoubleArray& weights) {
    MDagPath path;
    MObject skin_depend_node;
    find_by_name(polygon_name, path);
    find_by_name(skin_cluster_name, skin_depend_node);
    MFnSingleIndexedComponent fn_component;
    MObject components = fn_component.create(MFn::kMeshVertComponent);
    fn_component.addElements(vtx_ids);
    MFnSkinCluster fn_skin(skin_depend_node);
    fn_skin.getWeights(path, components, indices, weights);
}


void set_weights(MString polygon_name, MString skin_cluster_name, MIntArray& indices, MIntArray& vtx_ids, MDoubleArray& weights) {
    MDagPath path;
    MObject skin_depend_node;
    find_by_name(polygon_name, path);
    find_by_name(skin_cluster_name, skin_depend_node);
    MFnSingleIndexedComponent fn_component;
    MObject components = fn_component.create(MFn::kMeshVertComponent);
    fn_component.addElements(vtx_ids);
    MString command = "dgdirty " + skin_cluster_name;
    MGlobal::executeCommand(command);
    MFnSkinCluster fn_skin(skin_depend_node);
    fn_skin.setWeights(path, components, indices, weights);    
}

void set_weights(MString polygon_name, MString skin_cluster_name, MIntArray& indices, MDoubleArray& weights) {
    MDagPath path;
    MObject components;
    MObject skin_depend_node;
    find_by_name(polygon_name + ".vtx[*]", path, components);
    find_by_name(skin_cluster_name, skin_depend_node);
    MString command = "dgdirty " + skin_cluster_name;
    MGlobal::executeCommand(command);
    MFnSkinCluster fn_skin(skin_depend_node);
    fn_skin.setWeights(path, components, indices, weights);
}

void get_max_weights(MString polygon_name, MString skin_cluster_name, MIntArray& indices, MDoubleArray& max_weights) {
    MDoubleArray weights;
    get_weights(polygon_name, skin_cluster_name, indices, weights);
    int joint_length = indices.length();
    int vtx_length = weights.length() / joint_length;
    max_weights.setLength(vtx_length);
    tbb::parallel_for(0, vtx_length, 1, [joint_length, &weights, &max_weights](int vtx_id) {
        max_weights[vtx_id] = 0;
        int weight_id = vtx_id * joint_length;
        for (int joint_id = 0; joint_id < joint_length; joint_id++) {
            max_weights[vtx_id] += weights[weight_id + joint_id];
        }
    }
    );
}

void paint_eye(MString polygon_name, MString skin_cluster_name, MIntArray& indices, MPointArray& joint_points) {
    MDoubleArray max_weights;
    get_max_weights(polygon_name, skin_cluster_name, indices, max_weights);

    int vtx_length = max_weights.length();

    MDagPath dag_path;
    find_by_name(polygon_name, dag_path);
    MFnMesh fn_mesh(dag_path);
    MItMeshVertex mit_vtx(dag_path);

    set<int> find_vtx_ids;

    int joint_length = indices.length();
    vector<vector<vector<int>>> vtx_id_data;

    for (int joint_id = 0; joint_id < joint_length; joint_id++) {
        vtx_id_data.push_back(vector<vector<int>>());
        vtx_id_data[joint_id].push_back(vector<int>());
        MPoint closest_point;
        int face_id = 0;
        fn_mesh.getClosestPoint(joint_points[joint_id], closest_point, MSpace::kTransform, &face_id);
        MIntArray face_vtx_ids;
        fn_mesh.getPolygonVertices(face_id, face_vtx_ids);
        int face_vtx_length = face_vtx_ids.length();
        int closest_vtx_id = face_vtx_ids[0];
        MPoint face_vtx_point;
        fn_mesh.getPoint(closest_vtx_id, face_vtx_point);
        double min_distance = face_vtx_point.distanceTo(joint_points[joint_id]);
        for (int vtx_arr_id = 1; vtx_arr_id < face_vtx_length; vtx_arr_id++) {
            int face_vtx_id = face_vtx_ids[vtx_arr_id];
            fn_mesh.getPoint(face_vtx_id, face_vtx_point);
            double next_distance = face_vtx_point.distanceTo(joint_points[joint_id]);
            if (next_distance < min_distance) {
                min_distance = next_distance;
                closest_vtx_id = face_vtx_id;
            }
        }
        if (find_vtx_ids.count(closest_vtx_id) == 1) {
            continue;
        }

        vtx_id_data[joint_id][0].push_back(closest_vtx_id);
        find_vtx_ids.insert(closest_vtx_id);
        vector<int> pre_ids = vtx_id_data[joint_id][0];
    }
    for (int vtx_id = 0; vtx_id < vtx_length; vtx_id++) {
        for (int joint_id = 0; joint_id < joint_length; joint_id++) {
            vector<int> pre_ids = vtx_id_data[joint_id].back();
            if (pre_ids.size() == 0) {
                continue;
            }
            vtx_id_data[joint_id].push_back(vector<int>());
            for (auto pre_id: pre_ids) {
                MIntArray connect_vertices;
                int result_id = 0;
                mit_vtx.setIndex(pre_id, result_id);
                mit_vtx.getConnectedVertices(connect_vertices);
                int connect_vtx_length = connect_vertices.length();
                for (int connect_vertices_id = 0; connect_vertices_id < connect_vtx_length; connect_vertices_id++) {
                    int connect_vtx_id = connect_vertices[connect_vertices_id];
                    if (find_vtx_ids.count(connect_vtx_id) == 1) {
                        continue;
                    }
                    vtx_id_data[joint_id].back().push_back(connect_vtx_id);
                    find_vtx_ids.insert(connect_vtx_id);
                }
            }
        }
        if (find_vtx_ids.size() == vtx_length)
        {   
            break;
        }
        
    }
    MDoubleArray weights = MDoubleArray(joint_length * vtx_length, 0);
    for (int joint_id = 0; joint_id < joint_length; joint_id++) {
        for (auto vtx_ids : vtx_id_data[joint_id]) {
            for (auto vtx_id : vtx_ids) {
                weights[vtx_id * joint_length + joint_id] = max_weights[vtx_id];
            }
        }
    }
    set_weights(polygon_name, skin_cluster_name, indices, weights);
}



struct IdWeight {
    int i;
    double w;
    IdWeight(int ii, double ww) {
        i = ii;
        w = ww;
    }
};


void limit_max_influence(MString polygon_name, MString skin_cluster_name, MIntArray& indices, int max_influence) {
    MDoubleArray weights;
    get_weights(polygon_name, skin_cluster_name, indices, weights);

    int joint_length = indices.length();
    int vtx_length = weights.length() / joint_length;
    auto fun = [joint_length, max_influence, &weights](int vtx_id) {
        int weight_slice_id = vtx_id * joint_length;
        vector<IdWeight> iws;
        for (int joint_id = 0; joint_id < joint_length; joint_id++) {
            int weight_id = weight_slice_id + joint_id;
            iws.push_back(IdWeight(joint_id, weights[weight_id]));
            weights[weight_id] = 0;
        }
        auto camp = [](const IdWeight& iw1, const IdWeight& iw2) {return iw1.w > iw2.w; };
        sort(iws.begin(), iws.end(), camp);
        double max_weight = 0;
        for (int iw_id = 0; iw_id < max_influence; iw_id++) {
            max_weight += iws[iw_id].w;
        }
        for (int iw_id = 0; iw_id < max_influence; iw_id++) {
            weights[weight_slice_id + iws[iw_id].i] = iws[iw_id].w / max_weight;
        }

    };
    tbb::parallel_for(0, vtx_length, 1, fun);
    set_weights(polygon_name, skin_cluster_name, indices, weights);
}


void lock_influence_smooth(MString polygon_name, MString skin_cluster_name, MIntArray& indices, MIntArray vtx_ids, double smooth_step, int smooth_count) {
    int joint_length = indices.length();
    int vtx_length = vtx_ids.length();
    MDagPath polygon_dag_path;
    find_by_name(polygon_name, polygon_dag_path);
    MItMeshVertex mit_vtx(polygon_dag_path);
    set<int> grow_ids_set;
    map<int, MIntArray> id_connects;
    for (int vtx_index = 0; vtx_index < vtx_length; vtx_index++) {
        int vtx_id = vtx_ids[vtx_index];
        grow_ids_set.insert(vtx_id);
        MIntArray connect_vertices;
        int pre_id = 0;
        mit_vtx.setIndex(vtx_id, pre_id);
        mit_vtx.getConnectedVertices(connect_vertices);
        int connect_vtx_length = connect_vertices.length();
        for (int connect_vtx_id = 0; connect_vtx_id < connect_vtx_length; connect_vtx_id++) {
            grow_ids_set.insert(connect_vertices[connect_vtx_id]);
        }
        id_connects[vtx_id] = connect_vertices;
    }
    map<int, int> id_map;
    MIntArray grow_ids;
    int index = 0;
    for (auto i : grow_ids_set) {
        grow_ids.append(i);
        id_map[i] = index;
        index++;
    }

    MDoubleArray weights;
    get_weights(polygon_name, skin_cluster_name, indices, grow_ids, weights);
    for (int smooth_id = 0; smooth_id < smooth_count; smooth_id++) {
        MDoubleArray smooth_weights(weights);
        auto fun = [joint_length, &smooth_weights,&weights, &id_map, &vtx_ids, &id_connects, smooth_step](int i) {
            int vtx_id = vtx_ids[i];
            MIntArray connect_ids = id_connects[vtx_id];
            int weight_id = id_map[vtx_id] * joint_length;
            int connect_vtx_length = connect_ids.length();
            for (int joint_id = 0; joint_id < joint_length; joint_id++) {
                smooth_weights[weight_id + joint_id] = 0;
                for (int connect_id = 0; connect_id < connect_vtx_length; connect_id++) {
                    smooth_weights[weight_id + joint_id] += weights[id_map[connect_ids[connect_id]] * joint_length + joint_id];
                }
                smooth_weights[weight_id + joint_id] /= connect_vtx_length;
            }
            double sum_weight = 0.0;
            for (int joint_id = 0; joint_id < joint_length; joint_id++) {
                int i = weight_id + joint_id;
                double smooth_weight = smooth_weights[i];
                smooth_weights[i] = weights[i];
                if (smooth_weights[i] > 0.0001) {
                    smooth_weights[i] = smooth_weights[i] + (smooth_weight - smooth_weights[i]) * smooth_step;
                }
                sum_weight += smooth_weights[i];
            }
            for (int joint_id = 0; joint_id < joint_length; joint_id++) {
                smooth_weights[weight_id + joint_id] /= sum_weight;
            }
        };
        tbb::parallel_for(0, vtx_length, 1, fun);
        weights.copy(smooth_weights);
    }
    set_weights(polygon_name, skin_cluster_name, indices, grow_ids, weights);
}



map<string, vector<double>> cache_name_weights;

void copy_joint_weight(MString polygon_name, MString skin_cluster_name, MIntArray& indices, vector<string>& joint_names) {
    
    MDoubleArray weights;
    get_weights(polygon_name, skin_cluster_name, indices, weights);
    int joint_length = indices.length();
    int vtx_length = weights.length() / joint_length;
    cache_name_weights.clear();
    for (int joint_id = 0; joint_id < joint_length; joint_id++) {
        cache_name_weights[joint_names[joint_id]] = vector<double>(vtx_length, 0.0);
    }
    for (int vtx_id = 0; vtx_id < vtx_length; vtx_id++) {
        int weight_id = vtx_id * joint_length;
        for (int joint_id = 0; joint_id < joint_length; joint_id++) {
            cache_name_weights[joint_names[joint_id]][vtx_id] = weights[weight_id + joint_id];
        }
    }
}


void  paste_joint_weight(MString polygon_name, MString skin_cluster_name, MIntArray& indices, vector<string>& joint_names) {
    MDoubleArray weights;
    get_weights(polygon_name, skin_cluster_name, indices, weights);
    int joint_length = indices.length();
    int vtx_length = weights.length() / joint_length;
    vector<int> edit_ids;
    vector<int> keep_ids;
    for (int joint_id = 0; joint_id < joint_length; joint_id++) {
        if (cache_name_weights.count(joint_names[joint_id]) == 0) {
            keep_ids.push_back(joint_id);
        }
        else {
            edit_ids.push_back(joint_id);
        }
    }
    auto fun = [joint_length, &keep_ids, &weights, &edit_ids, &joint_names](int vtx_id) {
        int weight_id = vtx_id * joint_length;
        double keep_weight_sum = 0.0;
        double edit_weight_sum = 0.0;
        double cache_weight_sum = 0.0;
        for (auto keep_id : keep_ids) {
            keep_weight_sum += weights[weight_id + keep_id];
        }
        for (auto edit_id : edit_ids) {
            edit_weight_sum += weights[weight_id + edit_id];
            cache_weight_sum += cache_name_weights[joint_names[edit_id]][vtx_id];
            weights[weight_id + edit_id] = cache_name_weights[joint_names[edit_id]][vtx_id];
        }
        double weight_sum = keep_weight_sum + edit_weight_sum;
        double new_edit_weight_sum = min(weight_sum, cache_weight_sum);
        double new_keep_weight_sum = min(keep_weight_sum, weight_sum - new_edit_weight_sum);
        double edit_scale = cache_weight_sum < 0.00001 ? 0.0 : new_edit_weight_sum / cache_weight_sum;
        double keep_scale = keep_weight_sum < 0.00001 ? 0.0 : new_keep_weight_sum / keep_weight_sum;
        if (keep_ids.size() == 0) {
            edit_scale = cache_weight_sum < 0.00001 ? 0.0 : weight_sum / cache_weight_sum;
        }
        for (auto edit_id : edit_ids) {
            weights[weight_id + edit_id] = weights[weight_id + edit_id] * edit_scale;
        }
        for (auto keep_id : keep_ids) {
            weights[weight_id + keep_id] *= keep_scale;
        }
    };
    tbb::parallel_for(0, vtx_length, 1, fun);
    set_weights(polygon_name, skin_cluster_name, indices, weights);
}

PyToC4(paint_eye, MString, MString, MIntArray, MPointArray)
PyToC4(limit_max_influence, MString, MString, MIntArray, int)
PyToC4(copy_joint_weight, MString, MString, MIntArray, vector<string>)
PyToC4(paste_joint_weight, MString, MString, MIntArray, vector<string>)
PyToC6(lock_influence_smooth, MString, MString, MIntArray, MIntArray, double, int)


static PyMethodDef SpamMethods[] = {
    {"paint_eye",  paint_eye, METH_VARARGS, ""},
    {"limit_max_influence",  limit_max_influence, METH_VARARGS, ""},
    {"lock_influence_smooth",  lock_influence_smooth, METH_VARARGS, ""},
    {"copy_joint_weight",  copy_joint_weight, METH_VARARGS, ""},
    {"paste_joint_weight",  paste_joint_weight, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initweight_tool_api(void) {
    (void)Py_InitModule("weight_tool_api", SpamMethods);
}