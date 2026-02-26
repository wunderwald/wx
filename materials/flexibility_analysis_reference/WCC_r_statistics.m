

function [WCC_r_M_z, WCC_r_Var_z ] = WCC_r_statistics( WCC_r )


    % Fisher's z transformation of WCC_r values
    z = atanh(WCC_r);
    
    % average of tranformed cross-correlations
    WCC_r_M_z = mean( z );
    
    % variance of tranformed cross-correlations
    WCC_r_Var_z = var( z );