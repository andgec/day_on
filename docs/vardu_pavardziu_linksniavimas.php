<?php
 
/**
* Lietuviškų vardų linksniai.
*
* @author Dainius Kaupaitis <dainius at kaupaitis dot lt>
* @copyright Copyleft (ↄ) 2011, Dainius Kaupaitis
* @version 1.0
* @package Vardai
*/
class Linksniai {
 
        function __construct ( $encoding = 'UTF-8' ) {
       
                mb_internal_encoding($encoding) ;
               
                // kilmininkas (ko?)
                $this->kil = array(
                        'a' => 'os',
                        'as' => 'o',
                        'ė' => 'ės',
                        'tis' => 'čio',
                        'dis' => 'džio',
                        'is' => 'io',
                        'us' => 'aus',
                        'tys' => 'čio',
                        'dys' => 'džio',
                        'ys' => 'io'
                ) ;
               
                // naudininkas (kam?)
                $this->nau = array(
                        'a' => 'ai',
                        'as' => 'ui',
                        'ė' => 'ei',
                        'tis' => 'čiui',
                        'dis' => 'džiui',
                        'is' => 'iui',
                        'us' => 'ui',
                        'tys' => 'čiui',
                        'dys' => 'džiui',
                        'ys' => 'iui'
                ) ;
               
                // galininkas (ką?)
                $this->gal = array(
                        'a' => 'ą',
                        'as' => 'ą',
                        'ė' => 'ę',
                        'is' => 'į',
                        'us' => 'ų',
                        'ys' => 'į'
                ) ;
               
                // įnagininkas (kuo?)
                $this->ina = array(
                        'a' => 'a',
                        'as' => 'u',
                        'ė' => 'e',
                        'tis' => 'čiu',
                        'dis' => 'džiu',
                        'is' => 'iu',
                        'us' => 'u',
                        'tys' => 'čiu',
                        'dys' => 'džiu',
                        'ys' => 'iu'
                ) ;
               
                // vietininkas (kur? kame?)
                $this->vie = array(
                        'a' => 'oje',
                        'as' => 'e',
                        'ė' => 'ėje',
                        'is' => 'yje',
                        'us' => 'uje',
                        'ys' => 'yje'
                ) ;
               
                // šauksmininkas
                $this->sau = array(
                        'a' => 'a',
                        'as' => 'ai',
                        'ė' => 'e',
                        'is' => 'i',
                        'us' => 'au',
                        'ys' => 'y'
                ) ;
       
        }
       
        /**
        * Vardų transformacija
        *
        * @param string $vardas lietuviškas vardas arba pavardė
        * @param string $linksnis sutrumpintas linksnio pavadinimas: kil, nau, gal, ina, vie, sau
        * @return string
        */
        function getName ( $vardas, $linksnis = 'sau' ) {
       
                $vardai = explode( ' ', $this->sanitizeName($vardas) ) ;
                $vardaiL = array() ;
                foreach ( $vardai as $v ) {
                        $vardaiL[] = $this->getLinksnis( $v, $linksnis ) ;
                }
               
                return count($vardaiL) ? implode(' ', $vardaiL) : $vardas ;
       
        }
       
        /**
        * Vardų sanitarija
        *
        * @param string $vardas lietuviškas vardas arba pavardė
        * @return string
        */
        function sanitizeName ( $vardas ) {
       
                $vardas = mb_eregi_replace('[^a-ž]', ' ', $vardas) ;
                $vardas = mb_eregi_replace('\s+', ' ', $vardas) ;
                $vardas = trim($vardas) ;
                $vardas = mb_convert_case($vardas, MB_CASE_TITLE) ;
               
                return $vardas ;
       
        }
       
 
        /**
        * Vardas linksnyje
        *
        * @param string $vardas lietuviškas vardas arba pavardė
        * @param string $linksnis sutrumpintas linksnio pavadinimas: kil, nau, gal, ina, vie, sau
        * @return string
        */
        function getLinksnis ( $vardas, $linksnis = 'sau' ) {
       
                $return = $vardas ;
 
                foreach ( $this->$linksnis as $from=>$to ) {
                        if ( mb_substr( $return, -mb_strlen($from) ) == $from ) {
                                $return = mb_substr( $return, 0, -mb_strlen($from) ) ;
                                $return .= $to ;
                                break ;
                        }
                }
               
                return $return ;
               
        }
       
}
 
// testuojam
$l = new Linksniai ;
echo 'Laba diena, '.$l->getName('  antANAS bArAnAuskAS ---___') .'!' ;
 
?>
