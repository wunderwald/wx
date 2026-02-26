%% windowed cross-correlation 
% written and developed by Uwe Altmann
% Version from 30 July 2022


% For each window the algorithm computed the cross-correlation of time
% series parts, e.g. X1[10:110] and X2[10:110], and store all correlations
% in a vector. The correspoinding p-values are stored in a vector too.
% Furthermore the time points to which the cross-correlations refer are
% reported.
% Note, the time-lag is always zeor, no conclusions about leading are
% possible.


function [ WCC_t, WCC_r, WCC_p, input_arguments_ok ] = ...
         WCC( t, X1, X2, window_width, overlap)

% input:
% t: time vector, e.g. video frame or time in second
% X1: time series of peron 1 (continous data expected)
% X2: time series of peron 2 (continous data expected)
% window_width: size of windows, default is 125 = 5 sec in videos with 25
% frame per second
% overlap: overlap of subsequent windows, min = 0, max = window_width-1
%
% output:
% WCC_t: time points to which the WCC values refer
% WCC_r: windowed cross-correlation values
% WCC_p: corresponding p-value


%% *********************************************************************
%  some settings

input_arguments_ok = true ;



%% *********************************************************************
%  check input arguments 

    % all input parameter present?
    if nargin<5
        
        disp(' ')
        disp('Five input arguments needed: t, X1, X2, window_width, an overlap.')
        
        input_arguments_ok = false;
        
    end
    
    
    % have t and X1 and X2 the same length?
    if length(t) ~= length(X1) || length(t) ~= length(X2) 

        
        disp(' ')
        disp('t, X1, and X2 must have the same length.')
        
        input_arguments_ok = false;
        
    end
    
    
    
    % overlap < 0 or overlap >= window_width?
    if overlap < 0 || overlap >= window_width 

        
        disp(' ')
        disp('The overlap must be 1 or larger and smaller than window_width-1.')
        
        input_arguments_ok = false;
        
    end
    
    
    
    % window_width >= 50 and window_width < length(X1)?
    if window_width < 50 || window_width > length(X1)-2

        
        disp(' ')
        disp('The window_width must be >= 50 and < length(X1).')
        
        input_arguments_ok = false;
        
    end
    
%% *********************************************************************
% computation of WCC

if input_arguments_ok == false
    
    disp(' ')
    disp('Something is wrong with the input paramters. No WCC is computed. Output paremater are empthy accordingly.')

    WCC_t = [];
    WCC_r = [];
    WCC_p = [];
    
    
else
   
    disp(' ')
    disp('Computing WCC.')

    % begin and end of all windows
    window_shift = window_width - overlap;
    
    win_begin = [ 1:window_shift:(length(X1)-window_width) ]';
    
    win_end   = win_begin + window_width-1;
    
 
    % time points to which the WCC values refer (middle of windows)
    WCC_t = win_begin + floor( window_width / 2 );
    
    WCC_r = zeros( size( WCC_t) );
    
    WCC_p = ones( size( WCC_t) );
    
    
    
    % computation of WCC
    for k = 1:length(win_begin)
        
        R = [];
        P = [];
        
        
        [R,P] = corrcoef( X1( win_begin(k):win_end(k) ), ...
                          X2( win_begin(k):win_end(k) ), ...
                          'Rows', 'pairwise');
        
        WCC_r(k) = R(1,2);
        
        WCC_p(k) = P(1,2);
       
    end
    

    disp(' ')
    disp('Calculations done.')    
end
