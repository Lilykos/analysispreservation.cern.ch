import { Map, fromJS } from "immutable";

import {
  SCHEMA_INIT,
  CURRENT_UPDATE_CONFIG,
  CURRENT_UPDATE_PATH,
  CURRENT_UPDATE_SCHEMA_PATH,
  CURRENT_UPDATE_UI_SCHEMA_PATH,
  LIST_UPDATE,
  PROPERTY_SELECT,
  CREATE_MODE_ENABLE,
  ADD_PROPERTY,
  ADD_PROPERTY_INIT,
  SCHEMA_ERROR,
  SCHEMA_INIT_REQUEST
} from "../actions/schemaWizard";

const initialState = Map({
  list: {},
  selected: null,
  current: fromJS({
    schema: {},
    uiSchema: {}
  }),
  initial: fromJS({
    schema: {},
    uiSchema: {}
  }),
  config: {},
  field: null,
  propKeyEditor: null,
  editView: false,
  error: null,
  loader: false
});

export default function schemaReducer(state = initialState, action) {
  switch (action.type) {
    case SCHEMA_INIT_REQUEST:
      return state.set("loader", true);
    case SCHEMA_INIT:
      return state
        .set("selected", action.id)
        .set("current", fromJS(action.data))
        .set("initial", fromJS(action.data))
        .set("config", action.configs)
        .set("loader", false);
    case SCHEMA_ERROR:
      return state.set("error", action.payload).set("loader", false);
    case LIST_UPDATE:
      return state.set("list", Map(action.items));

    case ADD_PROPERTY_INIT:
      return state.set(
        "propKeyEditor",
        Map({ path: action.path, type: "new" })
      );
    case ADD_PROPERTY:
      return state
        .setIn(
          ["current", "schema", ...action.path, "properties", action.key],
          fromJS({})
        )
        .set("propKeyEditor", null);
    case PROPERTY_SELECT:
      return state.set(
        "field",
        fromJS({
          path: action.path.schema,
          uiPath: action.path.uiSchema
        }).set("editView", true)
      );
    // case PROPERTY_SELECT_CLEAR:
    //   return state.set("field", null);
    case CREATE_MODE_ENABLE:
      return state.set("field", null);
    case CURRENT_UPDATE_PATH:
      return state
        .setIn(
          ["current", "uiSchema", ...action.path.uiSchema],
          fromJS(action.value.uiSchema)
        )
        .setIn(
          ["current", "schema", ...action.path.schema],
          fromJS(action.value.schema)
        );
    case CURRENT_UPDATE_SCHEMA_PATH:
      return state.setIn(
        ["current", "schema", ...action.path],
        fromJS(action.value)
      );
    case CURRENT_UPDATE_UI_SCHEMA_PATH:
      return state.setIn(
        ["current", "uiSchema", ...action.path],
        fromJS(action.value)
      );
    case CURRENT_UPDATE_CONFIG:
      return state.set("config", action.config);
    default:
      return state;
  }
}
