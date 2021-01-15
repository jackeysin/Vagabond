import { createStore } from 'redux';

const initialState = {
    error: {
        visible: false,
        title: '',
        message: ''
    }
};

const reducer = (state = initialState, action) => {
    if (action.type === 'THROW_ERROR') {
        return {
            visible: true,
            title: action.title,
            message: action.message
        };
    } else if (action.type === 'HIDE_ERROR') {
        return initialState;
    }
}

const throwError = (title, message) => {
    return {
        type: 'THROW_ERROR',
        title: title,
        message: message
    };
}

const hideError = () => {
    return {
        type: 'HIDE_ERROR'
    };
}

const store = createStore(reducer);

export { store, throwError, hideError }